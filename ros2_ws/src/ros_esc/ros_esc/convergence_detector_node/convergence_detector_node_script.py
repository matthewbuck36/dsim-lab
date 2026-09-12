#!/usr/bin/env python3
import time

import numpy as np
import rclpy
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from ros_esc.clock_configuration import apply_legacy_sim_time_default
from ros_esc.convergence_detector_node.centroid_windows import (
    CentroidConfig,
    CentroidResult,
    CentroidWindowDetector,
)
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC
from ros_esc.convergence_detector_node.recurrent_geometry import (
    RecurrentConfig, RecurrentResult, RecurrentGeometryDetector, diagnostic_model_fields,
)
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES
from ros_esc.search_epoch import SearchEpochGate
from ros_esc.controller_node.clock_admission import ClockAdmission
from ros_esc.v2_lifecycle import hash_payload, message_payload
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CentroidConvergenceDiagnostics,
    StampedFloat64MultiArray,
)
from ros_esc.convergence_detector_node.centroid_contract import (
    CENTROID_METRIC_MODES, CENTROID_WINDOWS_V2, CENTROID_TWO_BLOCK_V2,
)


CROSSING_COUNT = "crossing_count"
QUALIFIED_DWELL = "qualified_dwell"
VALID_CONFIRMATION_POLICIES = (CROSSING_COUNT, QUALIFIED_DWELL)
PDE_MEAN_V1 = "pde_mean_v1"
VALID_METRIC_MODES = (PDE_MEAN_V1, *CENTROID_METRIC_MODES, RECURRENT_MODE)


class QualifiedDwellPolicy:
    """Accumulate qualified below-threshold time with hysteretic rearming."""

    def __init__(self, dwell_sec, exit_metric):
        self.dwell_sec = float(dwell_sec)
        self.exit_metric = float(exit_metric)
        if not np.isfinite(self.dwell_sec) or self.dwell_sec <= 0.0:
            raise ValueError("qualified dwell duration must be finite and positive")
        if not np.isfinite(self.exit_metric) or self.exit_metric <= 0.0:
            raise ValueError("qualified dwell exit metric must be finite and positive")
        self.reset()

    def reset(self):
        self.episode_active = False
        self.confirmed = False
        self.below_entry = False
        self.accumulated_sec = 0.0
        self.last_stamp_sec = None

    def update(self, stamp_sec, metric, qualified=True, valid=True):
        stamp_sec = float(stamp_sec)
        metric = float(metric)
        if (
            not valid
            or not qualified
            or not np.isfinite(stamp_sec)
            or not np.isfinite(metric)
        ):
            self.reset()
            return False
        if self.last_stamp_sec is not None and stamp_sec < self.last_stamp_sec:
            self.reset()
        if metric > self.exit_metric:
            self.reset()
            self.last_stamp_sec = stamp_sec
            return False

        if self.confirmed:
            self.last_stamp_sec = stamp_sec
            return False

        below_entry = metric < 0.0
        if below_entry:
            if not self.episode_active:
                self.episode_active = True
            if self.below_entry and self.last_stamp_sec is not None:
                self.accumulated_sec += stamp_sec - self.last_stamp_sec
            if self.accumulated_sec >= self.dwell_sec:
                self.confirmed = True
                self.below_entry = True
                self.last_stamp_sec = stamp_sec
                return True

        self.below_entry = below_entry
        self.last_stamp_sec = stamp_sec
        return False


def trajectory_motion_statistics(history):
    """Return finite path length, net displacement, and path efficiency."""
    points = np.asarray(history, dtype=np.float64)
    if (
        points.ndim != 2
        or points.shape[1] != 2
        or points.shape[0] < 2
        or not np.all(np.isfinite(points))
    ):
        raise ValueError(
            "trajectory history must contain at least two finite 2D points"
        )
    increments = np.diff(points, axis=0)
    path_length = float(np.sum(np.linalg.norm(increments, axis=1)))
    net_displacement = float(np.linalg.norm(points[-1] - points[0]))
    efficiency = net_displacement / path_length if path_length > 0.0 else 0.0
    return path_length, net_displacement, float(efficiency)


def motion_qualified(
    path_length,
    path_efficiency,
    minimum_path_length,
    maximum_path_efficiency,
):
    """Require a sufficiently long compact/orbiting trajectory."""
    values = (
        float(path_length),
        float(path_efficiency),
        float(minimum_path_length),
        float(maximum_path_efficiency),
    )
    if not all(np.isfinite(value) for value in values):
        return False
    return bool(
        path_length >= minimum_path_length
        and path_efficiency <= maximum_path_efficiency
    )


class ConvergenceDetector(Node):
    """
    Mean-based convergence metric using PDE transport buffer.

    For 2D:
      U is (N, 2) trajectory history.

      mean_recent = mean(U[0:M])
      mean_old    = mean(U[2M:3M])

      r = ||mean_recent - mean_old||^2

    metric = r + exp(-b*(t-t0)) - threshold

    A convergence candidate occurs when metric crosses below 0.

    A real convergence event is published only after the convergence counter
    reaches zero.
    """

    def __init__(self):
        super().__init__("convergence_detector")

        # MBuck 2026-08-04: retain the Gazebo default only when startup did
        # not explicitly select the physical wall clock.
        apply_legacy_sim_time_default(self)

        # ---------------------------------------------------------------------
        # Parameters
        # ---------------------------------------------------------------------

        self.declare_parameter("convergence_metric_mode", PDE_MEAN_V1)
        from ros_esc.v2_epoch import declare_epoch_parameters
        declare_epoch_parameters(self)
        self.declare_parameter("centroid_window_sec", 3.0)
        self.declare_parameter("centroid_epsilon_m", 0.06)
        self.declare_parameter("centroid_maximum_radius_m", 0.50)
        self.declare_parameter("centroid_maximum_gap_sec", 0.50)
        self.declare_parameter("centroid_pose_stale_sec", 0.50)
        self.declare_parameter("centroid_state_stale_sec", 0.50)
        self.declare_parameter("centroid_invalid_status_heartbeat_enabled", False)
        self.centroid_invalid_status_heartbeat_enabled = self.get_parameter(
            "centroid_invalid_status_heartbeat_enabled").value
        if type(self.centroid_invalid_status_heartbeat_enabled) is not bool:
            raise ValueError("centroid_invalid_status_heartbeat_enabled must be boolean")
        self.declare_parameter("recording_ready_required", False)
        self.declare_parameter(
            "recording_ready_topic", "/gesc_gaussian/recording_ready"
        )
        self.declare_parameter("recording_ready_stale_sec", 0.50)
        self.declare_parameter("pose_topic", "/odom")
        self.declare_parameter(
            "convergence_diagnostics_topic",
            "/gesc_gaussian/v2/convergence_diagnostics",
        )
        self.declare_parameter("recurrent_diagnostics_topic", RECURRENT_TOPIC)
        self.metric_mode = str(
            self.get_parameter("convergence_metric_mode").value
        ).strip().lower()
        if self.metric_mode not in VALID_METRIC_MODES:
            raise ValueError(
                "convergence_metric_mode must be one of "
                + ", ".join(VALID_METRIC_MODES)
            )
        self.recurrent_mode = self.metric_mode == RECURRENT_MODE
        self.centroid_mode = self.metric_mode in CENTROID_METRIC_MODES or self.recurrent_mode

        self.declare_parameter("k_periods", 20)

        # Threshold must be positive.
        self.declare_parameter("threshold", 0.1)
        self.declare_parameter("decay_rate", 0.15)

        # Must match PDEHistory omega and n_buffer.
        self.declare_parameter("n_buffer", 2000)
        self.declare_parameter("omega", 5.0)

        # Startup gating
        self.declare_parameter("min_fill_periods", 1.0)

        # ---------------------------------------------------------------------
        # New convergence-counter parameters
        # ---------------------------------------------------------------------

        # Number of convergence detections required before publishing
        # the fill-trigger event.
        self.declare_parameter("convergence_count_start", 3)

        # If True, after publishing a fill-ready event, reset the counter
        # so future local minima can also be detected and filled.
        self.declare_parameter("reset_counter_after_event", True)
        self.declare_parameter(
            "convergence_confirmation_policy",
            CROSSING_COUNT,
        )
        self.declare_parameter("convergence_confirmation_dwell_sec", 6.0)
        self.declare_parameter(
            "convergence_confirmation_exit_threshold_scale",
            1.5,
        )
        self.declare_parameter("enable_observability", False)
        self.declare_parameter(
            "algorithm_event_topic", "/gesc_gaussian/algorithm_events"
        )
        self.declare_parameter("algorithm_profile", "legacy")
        self.declare_parameter(
            "convergence_status_topic", "/gesc_gaussian/convergence_status"
        )
        self.declare_parameter("state_gating_enabled", False)
        self.declare_parameter(
            "algorithm_state_topic", "/gesc_gaussian/algorithm_state"
        )
        self.declare_parameter("minimum_path_length_m", 0.0)
        self.declare_parameter("maximum_path_efficiency", 1.0)

        self.k = int(self.get_parameter("k_periods").value)
        self.th = float(self.get_parameter("threshold").value)
        self.b = float(self.get_parameter("decay_rate").value)

        self.N = int(self.get_parameter("n_buffer").value)
        self.omega = float(self.get_parameter("omega").value)

        self.T = 2.0 * np.pi / self.omega
        self.kT = self.k * self.T
        self.dt_node = self.kT / self.N

        self.min_fill_periods = float(
            self.get_parameter("min_fill_periods").value
        )

        self.min_time_before_trigger = self.min_fill_periods * self.kT

        self.count_start = int(
            self.get_parameter("convergence_count_start").value
        )

        self.reset_counter_after_event = bool(
            self.get_parameter("reset_counter_after_event").value
        )
        self.confirmation_policy = str(
            self.get_parameter("convergence_confirmation_policy").value
        ).strip().lower()
        if self.confirmation_policy not in VALID_CONFIRMATION_POLICIES:
            raise ValueError(
                "convergence_confirmation_policy must be one of "
                + ", ".join(VALID_CONFIRMATION_POLICIES)
            )
        self.confirmation_dwell_sec = float(
            self.get_parameter("convergence_confirmation_dwell_sec").value
        )
        self.confirmation_exit_threshold_scale = float(
            self.get_parameter(
                "convergence_confirmation_exit_threshold_scale"
            ).value
        )
        if not np.isfinite(self.th) or self.th <= 0.0:
            raise ValueError("threshold must be finite and positive")
        if (
            not np.isfinite(self.confirmation_dwell_sec)
            or self.confirmation_dwell_sec <= 0.0
        ):
            raise ValueError(
                "convergence_confirmation_dwell_sec must be finite and positive"
            )
        if (
            not np.isfinite(self.confirmation_exit_threshold_scale)
            or self.confirmation_exit_threshold_scale <= 1.0
        ):
            raise ValueError(
                "convergence_confirmation_exit_threshold_scale must exceed one"
            )
        self.algorithm_profile = str(
            self.get_parameter("algorithm_profile").value
        ).strip()
        if self.algorithm_profile not in VALID_PROFILES:
            raise ValueError(
                f"algorithm_profile must be one of {VALID_PROFILES}; "
                f"received {self.algorithm_profile!r}"
            )
        self.robust_profile = self.algorithm_profile == ROBUST_PROFILE
        self.enable_observability = bool(
            self.get_parameter("enable_observability").value
        ) or self.robust_profile
        self.state_gating_enabled = bool(
            self.get_parameter("state_gating_enabled").value
        )
        if self.state_gating_enabled and not self.robust_profile:
            raise ValueError(
                "state_gating_enabled requires algorithm_profile="
                f"{ROBUST_PROFILE}"
            )
        if self.centroid_mode and (
            not self.robust_profile or not self.state_gating_enabled
        ):
            raise ValueError(
                f"{self.metric_mode} requires robust profile state gating"
            )
        if self.centroid_invalid_status_heartbeat_enabled and (
            self.metric_mode not in CENTROID_METRIC_MODES or self.get_parameter("use_sim_time").value is not True
        ):
            raise ValueError("centroid_invalid_status_heartbeat_enabled requires centroid simulation")
        if (
            self.confirmation_policy == QUALIFIED_DWELL
            and (not self.robust_profile or not self.state_gating_enabled)
        ):
            raise ValueError(
                "qualified-dwell confirmation requires robust profile state gating"
            )
        self.minimum_path_length_m = float(
            self.get_parameter("minimum_path_length_m").value
        )
        self.maximum_path_efficiency = float(
            self.get_parameter("maximum_path_efficiency").value
        )
        if (
            not np.isfinite(self.minimum_path_length_m)
            or self.minimum_path_length_m < 0.0
        ):
            raise ValueError("minimum_path_length_m must be finite and nonnegative")
        if (
            not np.isfinite(self.maximum_path_efficiency)
            or self.maximum_path_efficiency < 0.0
            or self.maximum_path_efficiency > 1.0
        ):
            raise ValueError("maximum_path_efficiency must be in [0, 1]")
        self.observability_configuration_published = False

        if self.count_start < 1:
            self.count_start = 1

        self.count_remaining = self.count_start

        # ---------------------------------------------------------------------
        # Internal state
        # ---------------------------------------------------------------------

        self.t0 = None
        self.first_time = None
        self.last_metric = None
        self.last_buffer_timestamp = None
        self.search_gate = SearchEpochGate(self.state_gating_enabled)
        self.qualified_dwell_policy = QualifiedDwellPolicy(
            self.confirmation_dwell_sec,
            self.th * (self.confirmation_exit_threshold_scale - 1.0),
        )
        self.centroid_detector = None
        self.centroid_publisher = None
        self.pose_subscriber = None
        self.v2_binding = None
        self.continuous_mode = str(self.get_parameter('continuous_search_mode').value)
        if self.continuous_mode not in ('stationary_v1', 'rolling_gesc_v2'):
            raise ValueError('unsupported continuous_search_mode')
        if self.continuous_mode == 'rolling_gesc_v2' and not self.state_gating_enabled:
            raise ValueError('rolling detector requires state gating')
        if self.recurrent_mode:
            if self.get_parameter('use_sim_time').value is not True:
                raise ValueError('recurrent geometry requires selected simulation')
            # The new stream always covers unavailability through the existing
            # watchdog. The old opt-in parameter retains its original meaning.
            self.centroid_invalid_status_heartbeat_enabled = True
        if self.centroid_mode:
            self._initialize_centroid_mode()

        # ---------------------------------------------------------------------
        # Subscribers
        # ---------------------------------------------------------------------

        self.sub = None
        if not self.centroid_mode and self.continuous_mode != 'rolling_gesc_v2':
            self.sub = self.create_subscription(
                StampedFloat64MultiArray,
                "/pde_history",
                self.buffer_cb,
                10
            )
        self.algorithm_state_subscriber = None
        if self.state_gating_enabled:
            self.algorithm_state_subscriber = self.create_subscription(
                AlgorithmState,
                str(self.get_parameter("algorithm_state_topic").value),
                self.algorithm_state_cb,
                10,
            )

        # ---------------------------------------------------------------------
        # Publishers
        # ---------------------------------------------------------------------

        # This is published only when the counter reaches zero.
        # The Gaussian-fill node should subscribe to this topic.
        self.pub = self.create_publisher(
            StampedFloat64MultiArray,
            "/convergence_event",
            10
        )

        self.pub_metric = self.create_publisher(
            StampedFloat64MultiArray,
            "/convergence_metric",
            10
        )

        self.pub_r = self.create_publisher(
            StampedFloat64MultiArray,
            "/convergence_r",
            10
        )

        # Optional diagnostic publisher for the counter.
        self.pub_count = self.create_publisher(
            StampedFloat64MultiArray,
            "/convergence_count",
            10
        )
        self.algorithm_event_publisher = None
        self.convergence_status_publisher = None
        if self.enable_observability:
            self.algorithm_event_publisher = self.create_publisher(
                AlgorithmEvent,
                str(self.get_parameter("algorithm_event_topic").value),
                10,
            )
        if self.robust_profile:
            self.convergence_status_publisher = self.create_publisher(
                StampedFloat64MultiArray,
                str(self.get_parameter("convergence_status_topic").value),
                10,
            )

        if self.continuous_mode == 'rolling_gesc_v2':
            from ros_esc.convergence_detector_node.v2_binding import V2DetectorBinding
            self.v2_binding = V2DetectorBinding(self)

        if self.centroid_mode:
            self.get_logger().info(
                f"ConvergenceDetector: {self.metric_mode}, "
                f"pose={self.centroid_pose_topic}, "
                f"window={self.centroid_config.window_seconds:.3f}s, "
                f"epsilon={self.centroid_config.epsilon_m:.3f}m, "
                f"radius={self.centroid_config.max_radius_m:.3f}m, "
                + ("fixed recurrent supports at6s endpoints, one confirmation per SEARCH epoch"
                 if getattr(self, 'recurrent_mode', False) else
                 "six source-time windows, one confirmation per SEARCH epoch")
            )
            return

        self.get_logger().info(
            f"ConvergenceDetector: k={self.k}, th={self.th}, b={self.b}, "
            f"N={self.N}, omega={self.omega:.3f}, dt_node={self.dt_node:.6f}, "
            f"min_trigger_time={self.min_time_before_trigger:.2f}s, "
            f"count_start={self.count_start}, "
            f"confirmation_policy={self.confirmation_policy}, "
            f"confirmation_dwell_sec={self.confirmation_dwell_sec:.3f}, "
            "confirmation_exit_threshold_scale="
            f"{self.confirmation_exit_threshold_scale:.3f}, "
            f"state_gating={self.state_gating_enabled}, "
            f"minimum_path_length_m={self.minimum_path_length_m:.3f}, "
            f"maximum_path_efficiency={self.maximum_path_efficiency:.3f}"
        )

    def _initialize_centroid_mode(self):
        """Configure the opt-in source-stamped detector without PDE inputs."""
        if getattr(self, 'recurrent_mode', False):
            self.centroid_config = RecurrentConfig(max_gap_seconds=float(
                self.get_parameter('centroid_maximum_gap_sec').value))
            self.centroid_detector = RecurrentGeometryDetector(self.centroid_config)
        else:
            self.centroid_config = CentroidConfig(
                metric_mode=self.metric_mode,
                window_seconds=float(self.get_parameter("centroid_window_sec").value),
                epsilon_m=float(self.get_parameter("centroid_epsilon_m").value),
                max_radius_m=float(
                    self.get_parameter("centroid_maximum_radius_m").value
                ),
                max_gap_seconds=float(
                    self.get_parameter("centroid_maximum_gap_sec").value
                ),
            )
            self.centroid_detector = CentroidWindowDetector(self.centroid_config)
        self.recording_ready_required = bool(
            self.get_parameter("recording_ready_required").value
        )
        self.recording_ready_stale_sec = float(
            self.get_parameter("recording_ready_stale_sec").value
        )
        self.recording_ready = False
        self.recording_ready_receipt_monotonic = None
        self.centroid_pose_stale_sec = float(
            self.get_parameter("centroid_pose_stale_sec").value
        )
        self.centroid_state_stale_sec = float(
            self.get_parameter("centroid_state_stale_sec").value
        )
        if not all(
            np.isfinite(value) and value > 0.0
            for value in (
                self.centroid_pose_stale_sec,
                self.centroid_state_stale_sec,
                self.recording_ready_stale_sec,
            )
        ):
            raise ValueError("centroid source/state freshness must be positive")
        self.centroid_pose_topic = str(self.get_parameter("pose_topic").value)
        if not self.centroid_pose_topic.strip():
            raise ValueError("centroid pose_topic must be nonempty")
        self.centroid_search_epoch = 0
        self.centroid_confirmation_sequence = 0
        self.centroid_confirmed_in_epoch = False
        self.centroid_epoch_started_ns = None
        self.centroid_state_receipt_ns = None
        self.centroid_state_receipt_steady_ns = None
        self.centroid_state_source_ns = None
        self.centroid_state_valid = False
        self.centroid_last_valid_state = None
        self.centroid_pose_receipt_ns = None
        self.centroid_pose_receipt_steady_ns = None
        self.centroid_pose_source_ns = None
        self.centroid_frame_id = ""
        self.centroid_run_id = ""
        self.centroid_admission = ClockAdmission()
        self.centroid_admission_generation = 0
        self.centroid_admission_last_now_ns = None
        self.centroid_admission_run_id = ""
        self.centroid_retired_run_ids = set()
        self.centroid_admission_frame = None
        self.centroid_state_fenced = False
        self.centroid_draining = False
        self.centroid_invalid_reason = "waiting_for_search"
        self.latest_centroid_result = None
        self.centroid_last_publication_ns = None
        self.centroid_last_publication_steady_ns = None
        self.centroid_last_publication_reason = None
        diagnostic_type = CentroidConvergenceDiagnostics
        diagnostic_topic_parameter = 'convergence_diagnostics_topic'
        if getattr(self, 'recurrent_mode', False):
            from ros_esc_interfaces.msg import RecurrentConvergenceDiagnostics
            diagnostic_type = RecurrentConvergenceDiagnostics
            diagnostic_topic_parameter = 'recurrent_diagnostics_topic'
        self.centroid_diagnostic_type = diagnostic_type
        self.centroid_publisher = self.create_publisher(
            diagnostic_type, str(self.get_parameter(diagnostic_topic_parameter).value), 10)

        self.pose_subscriber = self.create_subscription(
            Odometry, self.centroid_pose_topic, self.pose_cb, 10
        )
        self.recording_ready_subscriber = None
        if self.recording_ready_required:
            self.recording_ready_subscriber = self.create_subscription(
                Bool,
                str(self.get_parameter("recording_ready_topic").value),
                self._centroid_recording_ready_cb,
                10,
            )
        self.centroid_watchdog_period_sec = min(0.10, self.centroid_pose_stale_sec / 2.0)
        self.centroid_watchdog = self.create_timer(
            self.centroid_watchdog_period_sec,
            self._centroid_watchdog_cb,
            clock=Clock(clock_type=ClockType.STEADY_TIME),
        )

    def _centroid_now_ns(self):
        return self.get_clock().now().nanoseconds

    @staticmethod
    def _centroid_stamp_ns(stamp):
        seconds, nanoseconds = int(stamp.sec), int(stamp.nanosec)
        if seconds < 0 or not 0 <= nanoseconds < 1_000_000_000:
            return None
        return seconds * 1_000_000_000 + nanoseconds

    @staticmethod
    def _centroid_time(stamp_ns):
        message = Time()
        if stamp_ns is not None and stamp_ns >= 0:
            message.sec = int(stamp_ns // 1_000_000_000)
            message.nanosec = int(stamp_ns % 1_000_000_000)
        return message

    def _centroid_limit_ns(self, kind):
        seconds = (self.centroid_state_stale_sec if kind == "state"
                   else self.centroid_pose_stale_sec)
        return round(seconds * 1e9)

    def _centroid_clear_pending(self):
        # Retain frontiers: a discarded duplicate cannot refresh its lease.
        self.centroid_admission.discard("state")
        self.centroid_admission.discard("pose")
        self.centroid_admission_generation += 1

    def _centroid_check_clock(self, now_ns):
        previous = self.centroid_admission_last_now_ns
        self.centroid_admission_last_now_ns = now_ns
        if now_ns < 0 or (previous is not None and now_ns < previous):
            self._centroid_clear_pending()
            self.centroid_state_valid = False
            self.centroid_state_fenced = True
            self.search_gate.active = False
            self.centroid_pose_receipt_ns = None
            self.centroid_pose_receipt_steady_ns = None
            self._invalidate_centroid("centroid_clock_rollback")
            return False
        return True

    def _centroid_reject(self, kind, reason, source_ns=None):
        if kind == "state":
            self._centroid_clear_pending()
            self.centroid_state_valid = False
            self.centroid_state_fenced = True
            self.search_gate.active = False
        else:
            self.centroid_admission.discard("pose")
            self.centroid_pose_receipt_ns = None
            self.centroid_pose_receipt_steady_ns = None
        self._invalidate_centroid(reason, source_ns)

    def _centroid_algorithm_state_cb(self, msg):
        # Publication time and first subscriber receipts have separate roles.
        now_ns, steady_ns = self._centroid_now_ns(), time.monotonic_ns()
        if not self._centroid_check_clock(now_ns):
            return
        source_ns = None
        try:
            source_ns = self._centroid_stamp_ns(msg.stamp)
            run_id = str(msg.run_id)
            if (not msg.run_id_valid or not run_id.strip()
                    or msg.algorithm_profile != ROBUST_PROFILE
                    or (self.v2_binding is not None
                        and run_id != self.v2_binding.binding.run_id)
                    or run_id in self.centroid_retired_run_ids):
                raise ValueError("invalid_algorithm_identity")
            if source_ns is None or abs(now_ns - source_ns) > self._centroid_limit_ns("state"):
                raise ValueError("stale_or_future_algorithm_state")
            body_valid = bool(
                msg.state_valid and msg.state in range(
                    AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_FAILSAFE + 1)
                and (not msg.state_elapsed_valid or (
                    np.isfinite(msg.state_elapsed_sec)
                    and msg.state_elapsed_sec >= 0.0
                    and np.isfinite(msg.state_elapsed_sec * 1e9))))
            if run_id != self.centroid_admission_run_id:
                # Malformed prospective identities cannot retire a valid run.
                if not body_valid:
                    raise ValueError("invalid_algorithm_state")
                if len(self.centroid_retired_run_ids) >= 1024:
                    raise ValueError("algorithm_run_capacity")
                if self.centroid_admission_run_id:
                    self.centroid_retired_run_ids.add(self.centroid_admission_run_id)
                    self._centroid_clear_pending()
                    self.centroid_state_valid = False
                    self.search_gate.active = False
                    self._invalidate_centroid("algorithm_run_changed")
                self.centroid_admission.clear()
                self.centroid_admission_run_id = run_id
                self.centroid_admission_frame = None
            frontier = self.centroid_admission.frontier.get("state")
            if frontier is not None and source_ns < frontier[0]:
                raise ValueError("algorithm_state_time_rollback")
            # Invalid publications still fence older queued/retransmitted states.
            self.centroid_admission.receive(
                "state", source_ns, now_ns, steady_ns, msg,
                limit_ns=self._centroid_limit_ns("state"),
                fingerprint=hash_payload(message_payload(msg)))
            if not body_valid:
                raise ValueError("invalid_algorithm_state")
            if msg.state != AlgorithmState.STATE_SEARCH:
                # A known stop revokes support immediately, even before coverage.
                self.centroid_state_fenced = True
                self.search_gate.active = False
                self.centroid_admission.discard("pose")
                if self.centroid_invalid_reason != "outside_search":
                    self._invalidate_centroid("outside_search")
            self._centroid_drain_pending()
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            self._centroid_reject("state", str(error), source_ns)

    def _centroid_admit_state(self, item):
        msg, state_source_ns = item.message, item.source_ns
        run_changed = self.centroid_run_id != str(msg.run_id)
        entering_search = bool(
            msg.state == AlgorithmState.STATE_SEARCH
            and (run_changed or self.centroid_last_valid_state != AlgorithmState.STATE_SEARCH))
        previous_valid_state = self.centroid_last_valid_state
        self.centroid_run_id = str(msg.run_id)
        self.centroid_state_source_ns = state_source_ns
        self.centroid_state_receipt_ns = item.receipt_ns
        self.centroid_state_receipt_steady_ns = item.steady_ns
        self.centroid_state_valid = True
        self.centroid_last_valid_state = int(msg.state)
        self.centroid_state_fenced = any(
            queued.message.state != AlgorithmState.STATE_SEARCH
            for queued in self.centroid_admission.pending["state"])
        self.search_gate.active = msg.state == AlgorithmState.STATE_SEARCH
        self.search_gate.run_id = self.centroid_run_id
        if entering_search:
            self.centroid_search_epoch += 1
            self.centroid_confirmed_in_epoch = False
            self.centroid_epoch_started_ns = state_source_ns
            if msg.state_elapsed_valid:
                self.centroid_epoch_started_ns = max(
                    0, state_source_ns - round(msg.state_elapsed_sec * 1e9))
            # Run changes and non-SEARCH receipts already revoked old support.
            # Preserve new-epoch poses received behind this deferred SEARCH.
            pending = self.centroid_admission.pending["pose"]
            while pending and pending[0].source_ns < self.centroid_epoch_started_ns:
                pending.popleft()
            epoch_args = ({'start_ns': self.centroid_epoch_started_ns}
                          if getattr(self, 'recurrent_mode', False) else {})
            self.centroid_detector.start_epoch(
                f"{self.centroid_run_id}:{self.centroid_search_epoch}", **epoch_args)
            self.latest_centroid_result = None
            self.centroid_invalid_reason = "waiting_for_pose"
            self.centroid_pose_receipt_ns = None
            self.centroid_pose_receipt_steady_ns = None
            self.centroid_pose_source_ns = None
        elif (msg.state != AlgorithmState.STATE_SEARCH
              and (previous_valid_state == AlgorithmState.STATE_SEARCH or run_changed)):
            self.centroid_admission.discard("pose")
            if self.centroid_invalid_reason != "outside_search":
                self._invalidate_centroid("outside_search")

    def _centroid_drain_pending(self):
        if self.centroid_draining:
            return
        self.centroid_draining = True
        try:
            # Covered state revisions precede pose integration even when inactive.
            for kind in ("state", "pose"):
                if kind == "pose" and self.v2_binding is not None:
                    continue  # Rolling pose admission has exactly one owner.
                now_ns, steady_ns = self._centroid_now_ns(), time.monotonic_ns()
                if not self._centroid_check_clock(now_ns):
                    return
                generation = self.centroid_admission_generation
                try:
                    items = self.centroid_admission.covered(
                        kind, now_ns, steady_ns, limit_ns=self._centroid_limit_ns(kind))
                    for item in items:
                        now_ns, steady_ns = self._centroid_now_ns(), time.monotonic_ns()
                        if generation != self.centroid_admission_generation:
                            return
                        limit = self._centroid_limit_ns(kind)
                        if (not self._centroid_check_clock(now_ns)
                                or not 0 <= now_ns - item.source_ns <= limit
                                or not 0 <= now_ns - item.receipt_ns <= limit
                                or not 0 <= steady_ns - item.steady_ns <= limit):
                            raise ValueError("stale_pending_" + kind)
                        if kind == "state":
                            self._centroid_admit_state(item)
                        else:
                            previous_frame = self.centroid_admission_frame
                            self._admitted_pose_cb(
                                item.message, receipt_ns=item.receipt_ns,
                                receipt_steady_ns=item.steady_ns)
                            if (previous_frame is not None
                                    and previous_frame != self.centroid_admission_frame):
                                # A frame transition seeds the new history; all
                                # already queued support predates that boundary.
                                break
                except (TypeError, ValueError, OverflowError) as error:
                    self._centroid_reject(kind, str(error))
        finally:
            self.centroid_draining = False

    def _centroid_state_ready(self, now_ns):
        receipt, steady = (self.centroid_state_receipt_ns,
                           self.centroid_state_receipt_steady_ns)
        limit = self._centroid_limit_ns("state")
        return bool(
            self.search_gate.active and self.centroid_state_valid
            and not self.centroid_state_fenced
            and receipt is not None and steady is not None
            and 0 <= now_ns - receipt <= limit
            and 0 <= time.monotonic_ns() - steady <= limit
            and self.centroid_state_source_ns is not None
            and 0 <= now_ns - self.centroid_state_source_ns <= limit)

    def _centroid_pose_ready(self, now_ns):
        receipt, steady = (self.centroid_pose_receipt_ns,
                           self.centroid_pose_receipt_steady_ns)
        limit = self._centroid_limit_ns("pose")
        return bool(receipt is not None and steady is not None
                    and self.centroid_pose_source_ns is not None
                    and 0 <= now_ns - receipt <= limit
                    and 0 <= time.monotonic_ns() - steady <= limit
                    and 0 <= now_ns - self.centroid_pose_source_ns <= limit)

    def _centroid_recording_ready_cb(self, msg):
        self.recording_ready = bool(msg.data)
        self.recording_ready_receipt_monotonic = time.monotonic()
        if not self.recording_ready:
            self._centroid_clear_pending()
            if self.centroid_invalid_reason != "recording_not_ready":
                self._invalidate_centroid("recording_not_ready")

    def _centroid_recording_authorized(self):
        if not self.recording_ready_required:
            return True
        receipt = self.recording_ready_receipt_monotonic
        return bool(
            self.recording_ready
            and receipt is not None
            and 0 <= time.monotonic() - receipt <= self.recording_ready_stale_sec
        )

    def _invalidate_centroid(self, reason, source_ns=None, source_valid=False):
        if reason == "recording_not_ready":
            self._centroid_clear_pending()
        result = self.centroid_detector.invalidate(str(reason))
        self.latest_centroid_result = result
        self.centroid_invalid_reason = str(reason)
        self._publish_centroid_result(
            result, source_ns=source_ns, source_valid=source_valid
        )

    def _centroid_watchdog_cb(self):
        self._centroid_watchdog_checks()
        if self.centroid_invalid_status_heartbeat_enabled:
            self._centroid_invalid_status_heartbeat()

    def _centroid_watchdog_checks(self):
        self._centroid_drain_pending()
        if not self.search_gate.active:
            return
        now_ns = self._centroid_now_ns()
        if not self._centroid_recording_authorized():
            reason = "recording_not_ready"
        elif not self._centroid_state_ready(now_ns):
            reason = "stale_algorithm_state"
        elif self.centroid_pose_receipt_ns is None:
            return
        elif not self._centroid_pose_ready(now_ns):
            reason = "stale_pose"
        else:
            return
        if self.centroid_invalid_reason != reason:
            self._invalidate_centroid(reason, self.centroid_pose_source_ns)

    def _centroid_invalid_status_heartbeat(self):
        """Observe unavailability without changing numerical or receipt state."""
        now_ns, steady_ns = self._centroid_now_ns(), time.monotonic_ns()
        if now_ns < 0:
            return
        if not self._centroid_recording_authorized():
            reason = "recording_not_ready"
        elif (self.centroid_last_valid_state is not None
              and self.centroid_last_valid_state != AlgorithmState.STATE_SEARCH):
            reason = "outside_search"
        elif not self.search_gate.active:
            reason = "waiting_for_search"
        elif not self._centroid_state_ready(now_ns):
            reason = "stale_algorithm_state"
        elif self.v2_binding is not None and not self.v2_binding.binding.ready(now_ns):
            reason = "unavailable_rolling_binding"
        elif self.centroid_pose_receipt_ns is None:
            reason = "waiting_for_pose"
        elif not self._centroid_pose_ready(now_ns):
            reason = "stale_pose"
        elif self.v2_binding is not None and not self.v2_binding.centroid_ready(
                now_ns=now_ns, steady_ns=steady_ns):
            reason = "stale_selected_pose_receipt"
        else:
            return  # Healthy SEARCH remains entirely pose driven.
        last_steady = self.centroid_last_publication_steady_ns
        if (last_steady is not None
                and steady_ns-last_steady < self.centroid_watchdog_period_sec*1e9):
            return
        if (now_ns == self.centroid_last_publication_ns
                and reason == self.centroid_last_publication_reason):
            return  # A held clock does not need repeated identical status.
        # Never copy a full result or invalidate merely to report status: both
        # would alter the meaning or lifetime of actual SEARCH support.
        result_type = RecurrentResult if getattr(self, 'recurrent_mode', False) else CentroidResult
        result = result_type(epoch_id=self.centroid_detector.epoch_id,
            frame_id=self.centroid_frame_id, stamp_ns=None,
            reset_sequence=self.centroid_detector.reset_sequence, reset_reason=reason)
        self._publish_centroid_result(result, source_ns=None, source_valid=False)

    def pose_cb(self, msg):
        """Integrate selected odometry in absolute source time, SEARCH only."""
        if not self.centroid_mode:
            return
        if self.v2_binding is not None:
            self.v2_binding.receive_pose(msg)
            return
        now_ns, steady_ns = self._centroid_now_ns(), time.monotonic_ns()
        if not self._centroid_check_clock(now_ns):
            return
        source_ns = None
        try:
            source_ns = self._centroid_stamp_ns(msg.header.stamp)
            if source_ns is None:
                raise ValueError("invalid_pose_stamp")
            if abs(now_ns - source_ns) > self._centroid_limit_ns("pose"):
                raise ValueError("stale_or_future_pose")
            frame = str(msg.header.frame_id)
            xy = (float(msg.pose.pose.position.x), float(msg.pose.pose.position.y))
            if not frame.strip():
                raise ValueError("invalid_frame")
            if not np.all(np.isfinite(xy)):
                raise ValueError("invalid_position")
            if not self._centroid_recording_authorized():
                self._invalidate_centroid("recording_not_ready", source_ns)
                return
            self.centroid_admission.receive(
                "pose", source_ns, now_ns, steady_ns, msg,
                limit_ns=self._centroid_limit_ns("pose"), fingerprint=(frame, xy))
            self._centroid_drain_pending()
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            self._centroid_reject("pose", str(error), source_ns)

    def _admitted_pose_cb(self, msg, receipt_ns=None, receipt_steady_ns=None):
        """Run the unchanged metric after optional V2 source admission."""
        # The rolling binding can drain before this node's watchdog timer.
        # Its covered pose still requires the latest covered state revision.
        self._centroid_drain_pending()
        now_ns = self._centroid_now_ns()
        source_ns = self._centroid_stamp_ns(msg.header.stamp)
        self.centroid_pose_receipt_ns = now_ns if receipt_ns is None else receipt_ns
        self.centroid_pose_receipt_steady_ns = (
            receipt_steady_ns if receipt_steady_ns is not None else
            self.v2_binding.latest_pose_steady_ns if self.v2_binding is not None
            else time.monotonic_ns())
        self.centroid_pose_source_ns = source_ns
        self.centroid_frame_id = str(msg.header.frame_id)
        xy = (float(msg.pose.pose.position.x), float(msg.pose.pose.position.y))
        valid_source = bool(
            self.centroid_frame_id.strip() and np.all(np.isfinite(xy))
        )
        if source_ns is None:
            self._invalidate_centroid("invalid_pose_stamp")
            return
        if not 0 <= now_ns - source_ns <= self.centroid_pose_stale_sec * 1e9:
            self._invalidate_centroid("stale_or_future_pose", source_ns)
            return
        if not valid_source:
            reason = (
                "invalid_frame" if not self.centroid_frame_id.strip()
                else "invalid_position"
            )
            self._invalidate_centroid(reason, source_ns)
            return
        if not self._centroid_state_ready(now_ns):
            reason = (
                "outside_search"
                if not self.search_gate.active
                else "stale_algorithm_state"
            )
            self._invalidate_centroid(reason, source_ns, source_valid=True)
            return
        if not self._centroid_recording_authorized():
            self._invalidate_centroid("recording_not_ready", source_ns)
            return
        if source_ns < self.centroid_epoch_started_ns:
            self._invalidate_centroid("pre_epoch_pose", source_ns)
            return
        if self.v2_binding is None:
            if (self.centroid_admission_frame is not None
                    and self.centroid_admission_frame != self.centroid_frame_id):
                self.centroid_admission.discard("pose")
            self.centroid_admission_frame = self.centroid_frame_id
        if not self.observability_configuration_published:
            self._publish_event(
                AlgorithmEvent.EVENT_CONFIGURATION,
                f"{self.metric_mode} source-time configuration",
                source_timestamp=None,
                value_names=[
                    "centroid_window_sec", "centroid_epsilon_m",
                    "centroid_maximum_radius_m", "centroid_maximum_gap_sec",
                    "centroid_pose_stale_sec", "centroid_state_stale_sec",
                    "recording_ready_required", "recording_ready_stale_sec",
                ] + (["recurrent_status_heartbeat" if getattr(self, 'recurrent_mode', False)
                       else "centroid_invalid_status_heartbeat_enabled"]
                     if self.centroid_invalid_status_heartbeat_enabled else []),
                values=[
                    self.centroid_config.window_seconds,
                    self.centroid_config.epsilon_m,
                    self.centroid_config.max_radius_m,
                    self.centroid_config.max_gap_seconds,
                    self.centroid_pose_stale_sec, self.centroid_state_stale_sec,
                    float(self.recording_ready_required),
                    self.recording_ready_stale_sec,
                ] + ([1.] if self.centroid_invalid_status_heartbeat_enabled else []),
            )
            self.observability_configuration_published = True
        results = self.centroid_detector.update(
            source_ns, xy, self.centroid_frame_id
        )
        for result in results:
            self.latest_centroid_result = result
            self.centroid_invalid_reason = result.reset_reason
            if not self._publish_centroid_result(
                result, source_ns=source_ns, source_valid=valid_source
            ):
                # Authorization can expire while update evaluates boundaries.
                # None of this batch remains supported after invalidation.
                break

    def _publish_centroid_result(self, result, source_ns, source_valid):
        """Publish one snapshot; False means its update batch was invalidated."""
        recurrent = getattr(self, 'recurrent_mode', False)
        diagnostic = (self.centroid_diagnostic_type() if recurrent else CentroidConvergenceDiagnostics())
        now_ns = self._centroid_now_ns()
        diagnostic.stamp = self._centroid_time(now_ns)
        diagnostic.receipt_stamp = self._centroid_time(
            self.centroid_pose_receipt_ns
        )
        diagnostic.source_stamp = self._centroid_time(source_ns)
        diagnostic.epoch_started_at = self._centroid_time(
            self.centroid_epoch_started_ns
        )
        diagnostic.history_start = self._centroid_time(result.start_ns)
        diagnostic.history_end = self._centroid_time(result.end_ns)
        diagnostic.run_id = self.centroid_run_id
        diagnostic.frame_id = self.centroid_frame_id
        diagnostic.source_pose_topic = self.centroid_pose_topic
        diagnostic.metric_mode = self.metric_mode
        diagnostic.reset_reason = result.reset_reason
        diagnostic.search_epoch = self.centroid_search_epoch
        diagnostic.reset_sequence = result.reset_sequence
        if not recurrent:
            diagnostic.window_duration_sec = self.centroid_config.window_seconds
            diagnostic.epsilon_m = self.centroid_config.epsilon_m
        else:
            for key, value in diagnostic_model_fields(result).items():
                setattr(diagnostic, key, list(value) if isinstance(value, tuple) else value)
            diagnostic.persistence_start = self._centroid_time(result.persistence_start_ns)
        diagnostic.maximum_radius_m = self.centroid_config.max_radius_m
        diagnostic.score_m = (
            float(result.score_m) if result.score_m is not None else float("nan")
        )
        diagnostic.confinement_radius_m = (
            float(result.radius_m) if result.radius_m is not None else float("nan")
        )
        mean_xy = result.mean_xy if result.mean_xy is not None else (np.nan, np.nan)
        diagnostic.center_x_m = float(mean_xy[0])
        diagnostic.center_y_m = float(mean_xy[1])
        diagnostic.represented_duration_sec = result.represented_duration_ns * 1e-9
        diagnostic.maximum_source_gap_sec = result.max_source_gap_ns * 1e-9
        diagnostic.sample_count = result.sample_count
        if not recurrent:
            diagnostic.completed_window_count = len(result.centroids)
            diagnostic.window_start = [
                self._centroid_time(start) for start, _ in result.window_bounds_ns
            ]
            diagnostic.window_end = [
                self._centroid_time(end) for _, end in result.window_bounds_ns
            ]
            diagnostic.centroid_x_m = [float(point[0]) for point in result.centroids]
            diagnostic.centroid_y_m = [float(point[1]) for point in result.centroids]
            diagnostic.displacement_m = [float(value) for value in result.deltas_m]
        diagnostic.source_valid = bool(source_valid)
        diagnostic.history_valid = bool(source_valid and result.full)
        diagnostic.metric_valid = bool(
            diagnostic.history_valid
            and result.score_m is not None
            and np.isfinite(result.score_m)
        )
        diagnostic.confinement_valid = bool(
            diagnostic.history_valid
            and result.radius_m is not None
            and np.isfinite(result.radius_m)
        )
        state_ready = self._centroid_state_ready(now_ns)
        pose_ready = self._centroid_pose_ready(now_ns)
        recording_authorized = self._centroid_recording_authorized()
        empty_status = (self.centroid_invalid_status_heartbeat_enabled
                        and result.stamp_ns is None and not source_valid
                        and not result.full and not result.sample_count
                        and not result.centroids and not result.represented_duration_ns)
        rolling_ready = self.v2_binding is None or (
            self.v2_binding.centroid_ready(now_ns=now_ns, steady_ns=time.monotonic_ns())
            if empty_status else self.v2_binding.centroid_ready())
        if result.stamp_ns is not None and not (
            state_ready and pose_ready and recording_authorized and rolling_ready
        ):
            reason = (
                "recording_not_ready" if not recording_authorized
                else "stale_selected_pose_receipt" if not rolling_ready
                else "outside_search" if not self.search_gate.active
                else "stale_pose" if not pose_ready
                else "stale_algorithm_state"
            )
            self._invalidate_centroid(reason, source_ns, source_valid=source_valid)
            return False
        diagnostic.eligible = bool(
            diagnostic.metric_valid and diagnostic.confinement_valid
            and result.eligible and state_ready and recording_authorized
        )
        # The core's confirmed_event is first numerical eligibility, which may
        # have been withheld on authorization loss. Only successful typed
        # publication consumes this node's SEARCH-epoch confirmation. A later
        # complete, freshly rebuilt history can publish without rearming core.
        diagnostic.confirmed = bool(
            diagnostic.eligible and result.window_completed
            and not self.centroid_confirmed_in_epoch
        )
        diagnostic.confirmation_sequence = (
            self.centroid_confirmation_sequence + int(diagnostic.confirmed)
        )
        if diagnostic.confirmed and self.v2_binding is not None:
            diagnostic.confirmed = self.v2_binding.publish_centroid(diagnostic)
            if not diagnostic.confirmed and not self.v2_binding.centroid_ready():
                self._invalidate_centroid('stale_selected_pose_receipt', source_ns)
                return False
            diagnostic.confirmation_sequence = (
                self.centroid_confirmation_sequence + int(diagnostic.confirmed))
        self.centroid_publisher.publish(diagnostic)
        if self.centroid_invalid_status_heartbeat_enabled:
            self.centroid_last_publication_ns = now_ns
            self.centroid_last_publication_steady_ns = time.monotonic_ns()
            self.centroid_last_publication_reason = diagnostic.reset_reason
        if diagnostic.confirmed:
            self.centroid_confirmation_sequence = diagnostic.confirmation_sequence
            self.centroid_confirmed_in_epoch = True
        if diagnostic.confirmed and self.algorithm_event_publisher is not None:
            # The legacy event timestamp means relative experiment time. V2's
            # typed diagnostic is the authoritative absolute-time confirmation.
            self._publish_event(
                AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED,
                ("recurrent geometry convergence confirmed; verification required" if recurrent
                 else "centroid-window convergence confirmed; verification required"),
                source_timestamp=None,
                value_names=[
                    "score_m", "confinement_radius_m", "fill_center_x_m",
                    "fill_center_y_m", "search_epoch", "confirmation_sequence",
                ],
                values=[
                    diagnostic.score_m, diagnostic.confinement_radius_m,
                    diagnostic.center_x_m, diagnostic.center_y_m,
                    float(diagnostic.search_epoch),
                    float(diagnostic.confirmation_sequence),
                ],
            )
        return True

    def _reset_detection_state(self):
        """Start a fresh detector epoch and convergence counter."""
        self.t0 = None
        self.first_time = None
        self.last_metric = None
        self.last_buffer_timestamp = None
        self.count_remaining = self.count_start
        self.qualified_dwell_policy.reset()

    def algorithm_state_cb(self, msg):
        """Reset on every typed SEARCH boundary and disarm outside SEARCH."""
        if self.centroid_mode:
            self._centroid_algorithm_state_cb(msg)
            return
        boundary = self.search_gate.update(msg)
        if boundary in (SearchEpochGate.ENTERED, SearchEpochGate.LEFT):
            self._reset_detection_state()

    def buffer_cb(self, msg: StampedFloat64MultiArray):
        if self.centroid_mode:
            return
        t = float(msg.timestamp)
        if self.confirmation_policy == QUALIFIED_DWELL:
            if not np.isfinite(t):
                self._reset_detection_state()
                return
            if (
                self.last_buffer_timestamp is not None
                and t < self.last_buffer_timestamp
            ):
                self._reset_detection_state()
            self.last_buffer_timestamp = t

        if (
            self.enable_observability
            and not self.observability_configuration_published
        ):
            self._publish_event(
                AlgorithmEvent.EVENT_CONFIGURATION,
                "convergence detector configuration",
                source_timestamp=None,
                value_names=[
                    "k_periods",
                    "threshold",
                    "decay_rate",
                    "n_buffer",
                    "omega_rad_sec",
                    "min_fill_periods",
                    "convergence_count_start",
                    "qualified_dwell_policy",
                    "convergence_confirmation_dwell_sec",
                    "convergence_confirmation_exit_threshold_scale",
                    "state_gating_enabled",
                    "minimum_path_length_m",
                    "maximum_path_efficiency",
                ],
                values=[
                    float(self.k),
                    self.th,
                    self.b,
                    float(self.N),
                    self.omega,
                    self.min_fill_periods,
                    float(self.count_start),
                    (
                        1.0
                        if self.confirmation_policy == QUALIFIED_DWELL
                        else 0.0
                    ),
                    self.confirmation_dwell_sec,
                    self.confirmation_exit_threshold_scale,
                    1.0 if self.state_gating_enabled else 0.0,
                    self.minimum_path_length_m,
                    self.maximum_path_efficiency,
                ],
            )
            self.observability_configuration_published = True

        if not self.search_gate.active:
            return

        if self.first_time is None:
            self.first_time = t

        # ---------------------------------------------------------------------
        # Parse flat buffer:
        #
        #   [x0, y0, x1, y1, x2, y2, ...]
        #
        # into:
        #
        #   U.shape = (N, 2)
        # ---------------------------------------------------------------------

        data = np.array(msg.data, dtype=np.float64)

        if data.size < 2:
            if self.confirmation_policy == QUALIFIED_DWELL:
                self.qualified_dwell_policy.reset()
            return

        if data.size % 2 != 0:
            if self.confirmation_policy == QUALIFIED_DWELL:
                self.qualified_dwell_policy.reset()
            return

        U = data.reshape(-1, 2)

        if not np.all(np.isfinite(U)):
            if self.confirmation_policy == QUALIFIED_DWELL:
                self.qualified_dwell_policy.reset()
            return

        N = U.shape[0]

        if N < self.k * 3:
            if self.confirmation_policy == QUALIFIED_DWELL:
                self.qualified_dwell_policy.reset()
            return

        M = N // self.k

        if 3 * M > N or M <= 0:
            if self.confirmation_policy == QUALIFIED_DWELL:
                self.qualified_dwell_policy.reset()
            return

        # ---------------------------------------------------------------------
        # Startup gating
        # ---------------------------------------------------------------------

        if (t - self.first_time) < self.min_time_before_trigger:
            return

        if self.t0 is None:
            self.t0 = t
            return

        # ---------------------------------------------------------------------
        # Recent and old trajectory segments
        # ---------------------------------------------------------------------

        seg_recent = U[0:M, :]
        seg_old = U[2 * M:3 * M, :]
        motion_history = U[0:3 * M, :]
        (
            path_length,
            net_displacement,
            path_efficiency,
        ) = trajectory_motion_statistics(motion_history)
        if not motion_qualified(
            path_length,
            path_efficiency,
            self.minimum_path_length_m,
            self.maximum_path_efficiency,
        ):
            self.t0 = t
            self.last_metric = None
            if self.confirmation_policy == QUALIFIED_DWELL:
                self.qualified_dwell_policy.reset()
            return

        mean_recent = np.mean(seg_recent, axis=0)
        mean_old = np.mean(seg_old, axis=0)

        diff_mean = mean_recent - mean_old

        # Squared Euclidean distance between mean positions
        r_val = float(np.sum(diff_mean * diff_mean))

        decay_term = float(np.exp(-self.b * (t - self.t0)))

        metric = r_val + decay_term - self.th

        # ---------------------------------------------------------------------
        # Publish diagnostic metric
        # ---------------------------------------------------------------------

        metric_msg = StampedFloat64MultiArray()
        metric_msg.header = "CONV_METRIC"
        metric_msg.timestamp = t
        metric_msg.data = [float(metric)]
        self.pub_metric.publish(metric_msg)

        r_msg = StampedFloat64MultiArray()
        r_msg.header = "R_VAL"
        r_msg.timestamp = t
        r_msg.data = [float(r_val)]
        self.pub_r.publish(r_msg)

        if self.confirmation_policy == QUALIFIED_DWELL:
            self.count_remaining = (
                0 if self.qualified_dwell_policy.confirmed else 1
            )
        count_msg = StampedFloat64MultiArray()
        count_msg.header = "CONV_COUNT"
        count_msg.timestamp = t
        count_msg.data = [float(self.count_remaining)]
        self.pub_count.publish(count_msg)

        status_msg = None
        if self.convergence_status_publisher is not None:
            status_msg = StampedFloat64MultiArray()
            status_msg.header = "CONVERGENCE_STATUS"
            status_msg.timestamp = t
            status_msg.data = [
                float(metric),
                float(r_val),
                float(decay_term),
                float(mean_recent[0]),
                float(mean_recent[1]),
                float(mean_old[0]),
                float(mean_old[1]),
                float(self.count_remaining),
            ]
            if self.v2_binding is None:
                self.convergence_status_publisher.publish(status_msg)

        def publish_moving_status():
            # The moving typed confirmation copies the post-decision counter.
            # Publish its exact canonical observation once, including ordinary
            # non-confirming callbacks, before any confirmation/reset. Keep the
            # historical stationary publication order unchanged.
            if status_msg is not None and self.v2_binding is not None:
                status_msg.data[-1] = float(self.count_remaining)
                self.convergence_status_publisher.publish(status_msg)

        if self.confirmation_policy == QUALIFIED_DWELL:
            episode_was_active = self.qualified_dwell_policy.episode_active
            confirmed = self.qualified_dwell_policy.update(
                t,
                metric,
                qualified=True,
                valid=True,
            )
            candidate_entered = bool(
                not episode_was_active
                and self.qualified_dwell_policy.episode_active
            )
            self.count_remaining = (
                0 if self.qualified_dwell_policy.confirmed else 1
            )
            publish_moving_status()
            if candidate_entered and self.enable_observability:
                self._publish_event(
                    AlgorithmEvent.EVENT_CONVERGENCE_CANDIDATE,
                    "qualified-dwell convergence candidate",
                    source_timestamp=t,
                    value_names=[
                        "metric",
                        "r_mean_m2",
                        "decay",
                        "mean_recent_x_m",
                        "mean_recent_y_m",
                        "mean_old_x_m",
                        "mean_old_y_m",
                        "count_remaining",
                        "path_length_m",
                        "net_displacement_m",
                        "path_efficiency",
                        "qualified_dwell_elapsed_sec",
                        "qualified_dwell_required_sec",
                    ],
                    values=[
                        metric,
                        r_val,
                        decay_term,
                        float(mean_recent[0]),
                        float(mean_recent[1]),
                        float(mean_old[0]),
                        float(mean_old[1]),
                        float(self.count_remaining),
                        path_length,
                        net_displacement,
                        path_efficiency,
                        self.qualified_dwell_policy.accumulated_sec,
                        self.confirmation_dwell_sec,
                    ],
                )
            if confirmed:
                self._publish_confirmation(
                    t,
                    metric,
                    r_val,
                    decay_term,
                    mean_recent,
                    mean_old,
                    path_length,
                    net_displacement,
                    path_efficiency,
                    qualified_dwell_elapsed_sec=(
                        self.qualified_dwell_policy.accumulated_sec
                    ),
                )
            return

        # ---------------------------------------------------------------------
        # Crossing logic
        # ---------------------------------------------------------------------

        if self.last_metric is None:
            self.last_metric = metric
            publish_moving_status()
            return

        crossed = self.last_metric > 0.0 and metric < 0.0
        self.last_metric = metric

        if not crossed:
            publish_moving_status()
            return

        # ---------------------------------------------------------------------
        # A convergence candidate was detected.
        # Decrement the counter.
        # ---------------------------------------------------------------------

        self.count_remaining -= 1
        publish_moving_status()

        self.get_logger().info(
            "Convergence candidate: "
            + f"metric={metric:.6f}, "
            + f"r_mean={r_val:.6f}, "
            + f"decay={decay_term:.6f}, "
            + f"mean_recent=({mean_recent[0]:.4f}, {mean_recent[1]:.4f}), "
            + f"mean_old=({mean_old[0]:.4f}, {mean_old[1]:.4f}), "
            + f"count_remaining={self.count_remaining}, "
            + f"t={t:.3f}"
        )

        # Publish updated counter immediately
        count_msg = StampedFloat64MultiArray()
        count_msg.header = "CONV_COUNT_DECREMENTED"
        count_msg.timestamp = t
        count_msg.data = [float(self.count_remaining)]
        self.pub_count.publish(count_msg)

        if self.enable_observability:
            self._publish_event(
                AlgorithmEvent.EVENT_CONVERGENCE_CANDIDATE,
                "convergence candidate",
                source_timestamp=t,
                value_names=[
                    "metric",
                    "r_mean_m2",
                    "decay",
                    "mean_recent_x_m",
                    "mean_recent_y_m",
                    "mean_old_x_m",
                    "mean_old_y_m",
                    "count_remaining",
                    "path_length_m",
                    "net_displacement_m",
                    "path_efficiency",
                ],
                values=[
                    metric,
                    r_val,
                    decay_term,
                    float(mean_recent[0]),
                    float(mean_recent[1]),
                    float(mean_old[0]),
                    float(mean_old[1]),
                    float(self.count_remaining),
                    path_length,
                    net_displacement,
                    path_efficiency,
                ],
            )

        # Reset decay reference after every candidate, so the next candidate
        # requires another period of stable behavior.
        self.t0 = t
        self.last_metric = None

        # ---------------------------------------------------------------------
        # Only publish the actual convergence event when the counter reaches zero.
        # This is the event your Gaussian-fill node should use.
        # ---------------------------------------------------------------------

        if self.count_remaining <= 0:
            self._publish_confirmation(
                t,
                metric,
                r_val,
                decay_term,
                mean_recent,
                mean_old,
                path_length,
                net_displacement,
                path_efficiency,
            )

            if self.reset_counter_after_event:
                self.count_remaining = self.count_start

                self.get_logger().info(
                    f"Convergence counter reset to {self.count_start}"
                )

    def _publish_confirmation(
        self,
        source_timestamp,
        metric,
        r_val,
        decay_term,
        mean_recent,
        mean_old,
        path_length,
        net_displacement,
        path_efficiency,
        qualified_dwell_elapsed_sec=None,
    ):
        out = StampedFloat64MultiArray()
        out.header = "CONVERGED_FILL_READY"
        out.timestamp = float(source_timestamp)
        out.data = [
            float(metric),
            float(r_val),
            float(decay_term),
            float(mean_recent[0]),
            float(mean_recent[1]),
            float(mean_old[0]),
            float(mean_old[1]),
            float(self.count_remaining),
        ]
        if self.v2_binding is not None and not self.v2_binding.publish_legacy(out):
            self._reset_detection_state()
            return
        self.pub.publish(out)

        self.get_logger().info(
            "CONVERGED_FILL_READY: "
            + f"metric={metric:.6f}, "
            + f"r_mean={r_val:.6f}, "
            + f"decay={decay_term:.6f}, "
            + f"fill_center=({mean_recent[0]:.4f}, {mean_recent[1]:.4f}), "
            + f"t={source_timestamp:.3f}"
        )

        if not self.enable_observability:
            return
        value_names = [
            "metric",
            "r_mean_m2",
            "decay",
            "fill_center_x_m",
            "fill_center_y_m",
            "mean_old_x_m",
            "mean_old_y_m",
            "count_remaining",
            "path_length_m",
            "net_displacement_m",
            "path_efficiency",
        ]
        values = [
            metric,
            r_val,
            decay_term,
            float(mean_recent[0]),
            float(mean_recent[1]),
            float(mean_old[0]),
            float(mean_old[1]),
            float(self.count_remaining),
            path_length,
            net_displacement,
            path_efficiency,
        ]
        if qualified_dwell_elapsed_sec is not None:
            value_names.extend(
                [
                    "qualified_dwell_elapsed_sec",
                    "qualified_dwell_required_sec",
                ]
            )
            values.extend(
                [
                    float(qualified_dwell_elapsed_sec),
                    self.confirmation_dwell_sec,
                ]
            )
        self._publish_event(
            AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED,
            "convergence confirmed; fill ready",
            source_timestamp=source_timestamp,
            value_names=value_names,
            values=values,
        )

    def _publish_event(
        self,
        event_type,
        detail,
        source_timestamp,
        value_names,
        values,
        reason_code=0,
    ):
        """Publish a typed mirror without changing convergence state."""

        event = AlgorithmEvent()
        event.stamp = self.get_clock().now().to_msg()
        if source_timestamp is None:
            event.source_timestamp = float("nan")
            event.source_timestamp_valid = False
        else:
            event.source_timestamp = float(source_timestamp)
            event.source_timestamp_valid = bool(np.isfinite(source_timestamp))
        event.event_type = event_type
        event.state = AlgorithmState.STATE_UNAVAILABLE
        event.state_name = "UNAVAILABLE"
        event.state_valid = False
        event.fill_id = 0
        event.fill_id_valid = False
        event.reason_code = reason_code
        event.detail = detail
        event.value_names = list(value_names)
        event.values = [float(value) for value in values]
        self.algorithm_event_publisher.publish(event)


def main():
    rclpy.init()
    node = ConvergenceDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
