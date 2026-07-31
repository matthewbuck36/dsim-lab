#!/usr/bin/env python3

from collections import deque
import math
import time

import rclpy
import numpy as np
from nav_msgs.msg import Odometry
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
import rclpy.parameter
from scipy.optimize import least_squares

from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    GaussianFill as GaussianFillMessage,
    StampedFloat64MultiArray,
)
from std_msgs.msg import Float64MultiArray
from ros_esc.gaussian_fill_node.basin_estimator import (
    CostSnapshot,
    EstimatorConfig,
    FilteredWindow,
    PoseSnapshot,
    estimate_basin,
    freeze_sample_window,
    synchronize_samples,
)
from ros_esc.gaussian_fill_node.fill_designer import (
    FillDesignConfig,
    candidate_amplitude_floor,
    design_fill,
    initial_fill_geometry,
)
from ros_esc.gaussian_fill_node.fill_registry import (
    FillRegistry,
    RegistryConfig,
)
from ros_esc.supervisor_node.state_machine import (
    ROBUST_PROFILE,
    VALID_PROFILES,
    decode_candidate_informed_fill_payload,
)


ROBUST_FILL_CREATE = "ROBUST_FILL_CREATE"
ROBUST_FILL_REDESIGN_PREFIX = "ROBUST_FILL_REDESIGN:"


def robust_fill_redesign_target(header):
    """Return a positive targeted fill ID; older headers remain create requests."""

    text = str(header).strip()
    if not text.startswith(ROBUST_FILL_REDESIGN_PREFIX):
        return None
    suffix = text[len(ROBUST_FILL_REDESIGN_PREFIX):]
    try:
        target = int(suffix)
    except ValueError:
        return None
    return target if target > 0 else None


def retained_redesign_window(fill_registry, fill_id):
    """Return one immutable active-cluster sample window for redesign."""
    cluster = fill_registry.active_cluster_for_fill(fill_id)
    if cluster is None:
        return None
    samples = tuple(cluster.samples)
    return FilteredWindow(
        samples=samples,
        input_count=len(samples),
        rejected={},
    )


class GaussianFill(Node):
    """
    Adds Gaussian fills at detected trap locations.

    - Reads 2D position history from /pde_history as [x0,y0,x1,y1,...].
    - Reads PDE cost history from /pde_cost_history.
    - On /convergence_event, fits an inverted Gaussian basin to history:
      A * exp(-||xy - mu||^2 / v) + c ~= -J(xy).
    - Uses the convergence event mean as the default fill center. The fit is
      still used as a basin-quality check and sigma estimate.
    - Publishes /cost_bias: [A, mu_x, mu_y, sigma].
    """

    def __init__(self):
        super().__init__("gaussian_fill")

        # Use Gazebo sim time
        self.set_parameters([
            rclpy.parameter.Parameter(
                "use_sim_time",
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])

        # ---- Parameters ----
        self.declare_parameter("escape_policy", "conditional_gaussian_fill")
        self.declare_parameter("amplitude", 5.0)
        self.declare_parameter("min_sigma", 0.10)
        self.declare_parameter("max_sigma", 5.0)
        self.declare_parameter("min_points", 50)
        self.declare_parameter("use_recent_fraction", 1.0)
        self.declare_parameter("max_fills", 1)
        self.declare_parameter("fill_cooldown_sec", 0.0)
        self.declare_parameter("min_distance_between_fills", 0.0)
        self.declare_parameter("min_event_center_distance_between_fills", 0.0)
        self.declare_parameter("center_source", "event_mean")
        self.declare_parameter("max_fit_center_distance_from_event", 0.75)
        self.declare_parameter("fit_min_amplitude", 0.15)
        self.declare_parameter("fit_max_amplitude", 10.0)
        self.declare_parameter("fit_offset_bound", 10.0)
        self.declare_parameter("enable_observability", False)
        self.declare_parameter(
            "gaussian_fill_diagnostics_topic", "/gesc_gaussian/gaussian_fills"
        )
        self.declare_parameter(
            "algorithm_event_topic", "/gesc_gaussian/algorithm_events"
        )
        self.declare_parameter("algorithm_profile", "legacy")
        self.declare_parameter("fill_request_topic", "/gesc_gaussian/fill_requests")

        # Robust estimator/designer/registry parameters. These do not affect
        # the legacy fit path.
        robust_defaults = {
            "pose_topic": "/odom",
            "source_cost_topic": "/gesc_gaussian/source_cost",
            "algorithm_state_topic": "/gesc_gaussian/algorithm_state",
            "estimation_channel_index": 0,
            "sample_sync_tolerance_sec": 0.05,
            "maximum_position_speed_mps": 0.20,
            "outlier_mad_threshold": 3.5,
            "maximum_cluster_samples": 4000,
            "estimation_window_sec": 8.0,
            "minimum_valid_samples": 40,
            "maximum_sample_age_sec": 12.0,
            "mean_shift_iterations": 5,
            "center_tolerance_m": 0.005,
            "position_kernel_bandwidth_m": 0.25,
            "cost_temperature_normalized": 0.05,
            "covariance_eigenvalue_min_m2": 0.0025,
            "covariance_eigenvalue_max_m2": 0.25,
            "quadratic_ridge_lambda": 1e-6,
            "quadratic_condition_number_max": 1e8,
            "center_cost_percentile": 10.0,
            "shoulder_cost_percentile": 80.0,
            "inner_mahalanobis_radius": 1.0,
            "minimum_basin_depth": 0.02,
            "covariance_scale": 2.5,
            "sigma_floor_m": 0.15,
            "sigma_ceiling_m": 1.25,
            "amplitude_depth_scale": 1.5,
            "amplitude_curvature_scale": 1.2,
            "amplitude_min": 0.10,
            "amplitude_max": 3.00,
            "validation_grid_points_per_axis": 41,
            "validation_support_sigma": 3.0,
            "maximum_design_escalations": 5,
            "amplitude_escalation_factor": 1.5,
            "width_escalation_factor": 1.25,
            "grid_minimum_tolerance": 1e-9,
            "support_sigma": 3.0,
            "exit_sigma": 2.5,
            "merge_bandwidth_m": 0.50,
            "merge_radius_scale": 2.0,
            "minimum_merge_probability": 0.60,
            "low_confidence_threshold": 0.60,
            'reuse_retained_samples_on_redesign': False,
            "candidate_informed_fill_enabled": False,
            "candidate_informed_fill_amplitude_scale": 1.0,
        }
        for name, value in robust_defaults.items():
            self.declare_parameter(name, value)

        # Legacy parameter retained so older launch files do not fail.
        # The published fill amplitude now comes directly from "amplitude";
        # fitted amplitude is used only as a basin-detection quality check.
        self.declare_parameter("use_pde_cost_mean_for_amplitude", True)

        self.escape_policy = self._normalize_policy(
            str(self.get_parameter("escape_policy").value)
        )

        self.A = max(0.0, float(self.get_parameter("amplitude").value))
        self.pde_cost_mean = self.A
        self.use_pde_cost_mean_for_amplitude = bool(
            self.get_parameter("use_pde_cost_mean_for_amplitude").value
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
        self.observability_configuration_published = False
        self.current_event_timestamp = None
        self.fit_min_amplitude = max(
            0.0,
            float(self.get_parameter("fit_min_amplitude").value)
        )
        self.fit_max_amplitude = max(
            self.fit_min_amplitude,
            float(self.get_parameter("fit_max_amplitude").value)
        )
        self.fit_offset_bound = max(
            0.0,
            float(self.get_parameter("fit_offset_bound").value)
        )

        self.min_sigma = float(self.get_parameter("min_sigma").value)
        self.max_sigma = float(self.get_parameter("max_sigma").value)

        if self.max_sigma < self.min_sigma:
            self.get_logger().warn(
                "max_sigma was smaller than min_sigma; using min_sigma for both."
            )
            self.max_sigma = self.min_sigma

        self.min_points = max(1, int(self.get_parameter("min_points").value))

        self.use_recent_fraction = float(
            self.get_parameter("use_recent_fraction").value
        )
        self.use_recent_fraction = float(np.clip(self.use_recent_fraction, 0.0, 1.0))

        self.max_fills = int(self.get_parameter("max_fills").value)

        self.fill_cooldown_sec = max(
            0.0,
            float(self.get_parameter("fill_cooldown_sec").value)
        )

        self.min_distance_between_fills = max(
            0.0,
            float(self.get_parameter("min_distance_between_fills").value)
        )

        self.min_event_center_distance_between_fills = max(
            0.0,
            float(
                self.get_parameter(
                    "min_event_center_distance_between_fills"
                ).value
            )
        )

        self.center_source = self._normalize_center_source(
            str(self.get_parameter("center_source").value)
        )

        self.max_fit_center_distance_from_event = max(
            0.0,
            float(
                self.get_parameter(
                    "max_fit_center_distance_from_event"
                ).value
            )
        )

        self.fill_count = 0
        self.has_filled = False
        self.last_fill_time = None
        self.fill_centers = []
        self.event_centers = []

        self.buf_xy = None
        self.buf_cost = None
        self.estimation_channel_index = int(
            self.get_parameter("estimation_channel_index").value
        )
        self.pose_snapshots = deque(maxlen=20000)
        self.cost_snapshots = deque(maxlen=20000)
        self.robust_request_diagnostics = None
        self.latest_algorithm_state = None
        self.reuse_retained_samples_on_redesign = bool(
            self.get_parameter('reuse_retained_samples_on_redesign').value
        )
        self.candidate_informed_fill_enabled = bool(
            self.get_parameter("candidate_informed_fill_enabled").value
        )
        self.candidate_informed_fill_amplitude_scale = self._parameter_float(
            "candidate_informed_fill_amplitude_scale"
        )
        if (
            not math.isfinite(self.candidate_informed_fill_amplitude_scale)
            or self.candidate_informed_fill_amplitude_scale <= 0.0
        ):
            raise ValueError(
                "candidate_informed_fill_amplitude_scale must be finite "
                "and positive"
            )
        self.estimator_config = None
        self.design_config = None
        self.fill_registry = None
        if self.robust_profile:
            self.estimator_config = EstimatorConfig(
                sample_sync_tolerance_sec=self._parameter_float(
                    "sample_sync_tolerance_sec"
                ),
                maximum_position_speed_mps=self._parameter_float(
                    "maximum_position_speed_mps"
                ),
                outlier_mad_threshold=self._parameter_float(
                    "outlier_mad_threshold"
                ),
                estimation_window_sec=self._parameter_float(
                    "estimation_window_sec"
                ),
                minimum_valid_samples=int(
                    self.get_parameter("minimum_valid_samples").value
                ),
                maximum_sample_age_sec=self._parameter_float(
                    "maximum_sample_age_sec"
                ),
                mean_shift_iterations=int(
                    self.get_parameter("mean_shift_iterations").value
                ),
                center_tolerance_m=self._parameter_float("center_tolerance_m"),
                position_kernel_bandwidth_m=self._parameter_float(
                    "position_kernel_bandwidth_m"
                ),
                cost_temperature_normalized=self._parameter_float(
                    "cost_temperature_normalized"
                ),
                covariance_eigenvalue_min_m2=self._parameter_float(
                    "covariance_eigenvalue_min_m2"
                ),
                covariance_eigenvalue_max_m2=self._parameter_float(
                    "covariance_eigenvalue_max_m2"
                ),
                quadratic_ridge_lambda=self._parameter_float(
                    "quadratic_ridge_lambda"
                ),
                quadratic_condition_number_max=self._parameter_float(
                    "quadratic_condition_number_max"
                ),
                center_cost_percentile=self._parameter_float(
                    "center_cost_percentile"
                ),
                shoulder_cost_percentile=self._parameter_float(
                    "shoulder_cost_percentile"
                ),
                inner_mahalanobis_radius=self._parameter_float(
                    "inner_mahalanobis_radius"
                ),
                minimum_basin_depth=self._parameter_float("minimum_basin_depth"),
            )
            self.design_config = FillDesignConfig(
                covariance_scale=self._parameter_float("covariance_scale"),
                sigma_floor_m=self._parameter_float("sigma_floor_m"),
                sigma_ceiling_m=self._parameter_float("sigma_ceiling_m"),
                amplitude_depth_scale=self._parameter_float(
                    "amplitude_depth_scale"
                ),
                amplitude_curvature_scale=self._parameter_float(
                    "amplitude_curvature_scale"
                ),
                amplitude_min=self._parameter_float("amplitude_min"),
                amplitude_max=self._parameter_float("amplitude_max"),
                validation_grid_points_per_axis=int(
                    self.get_parameter("validation_grid_points_per_axis").value
                ),
                validation_support_sigma=self._parameter_float(
                    "validation_support_sigma"
                ),
                maximum_design_escalations=int(
                    self.get_parameter("maximum_design_escalations").value
                ),
                amplitude_escalation_factor=self._parameter_float(
                    "amplitude_escalation_factor"
                ),
                width_escalation_factor=self._parameter_float(
                    "width_escalation_factor"
                ),
                grid_minimum_tolerance=self._parameter_float(
                    "grid_minimum_tolerance"
                ),
                support_sigma=self._parameter_float("support_sigma"),
                exit_sigma=self._parameter_float("exit_sigma"),
                low_confidence_threshold=self._parameter_float(
                    "low_confidence_threshold"
                ),
            )
            self.fill_registry = FillRegistry(
                RegistryConfig(
                    merge_bandwidth_m=self._parameter_float("merge_bandwidth_m"),
                    merge_radius_scale=self._parameter_float("merge_radius_scale"),
                    minimum_merge_probability=self._parameter_float(
                        "minimum_merge_probability"
                    ),
                    maximum_cluster_samples=int(
                        self.get_parameter("maximum_cluster_samples").value
                    ),
                )
            )

        # ---- Subscribers ----
        self.fill_request_callback_group = MutuallyExclusiveCallbackGroup()
        self.sub_conv = self.create_subscription(
            StampedFloat64MultiArray,
            (
                str(self.get_parameter("fill_request_topic").value)
                if self.robust_profile
                else "/convergence_event"
            ),
            self.trigger_cb,
            10,
            callback_group=self.fill_request_callback_group,
        )

        self.sub_buffer = self.create_subscription(
            StampedFloat64MultiArray,
            "/pde_history",
            self.buffer_cb,
            10,
            callback_group=self.fill_request_callback_group,
        )

        self.sub_cost_history = self.create_subscription(
            Float64MultiArray,
            "/pde_cost_history",
            self.cost_history_cb,
            10,
            callback_group=self.fill_request_callback_group,
        )
        self.sub_pose = None
        self.sub_source_cost = None
        self.sub_algorithm_state = None
        if self.robust_profile:
            self.sub_pose = self.create_subscription(
                Odometry,
                str(self.get_parameter("pose_topic").value),
                self.pose_cb,
                10,
                callback_group=self.fill_request_callback_group,
            )
            self.sub_source_cost = self.create_subscription(
                CostBreakdown,
                str(self.get_parameter("source_cost_topic").value),
                self.source_cost_cb,
                10,
                callback_group=self.fill_request_callback_group,
            )
            self.sub_algorithm_state = self.create_subscription(
                AlgorithmState,
                str(self.get_parameter("algorithm_state_topic").value),
                self.algorithm_state_cb,
                10,
                callback_group=self.fill_request_callback_group,
            )

        # ---- Publisher ----
        self.pub = self.create_publisher(
            StampedFloat64MultiArray,
            "/cost_bias",
            10
        )
        self.gaussian_fill_diagnostics_publisher = None
        self.algorithm_event_publisher = None
        if self.enable_observability:
            self.gaussian_fill_diagnostics_publisher = self.create_publisher(
                GaussianFillMessage,
                str(
                    self.get_parameter(
                        "gaussian_fill_diagnostics_topic"
                    ).value
                ),
                10,
            )
            self.algorithm_event_publisher = self.create_publisher(
                AlgorithmEvent,
                str(self.get_parameter("algorithm_event_topic").value),
                10,
            )

        self.get_logger().info(
            "GaussianFill ready (2D): "
            + f"policy={self.escape_policy}, "
            + f"fallback_A={self.A:.3f}, "
            + f"fit_A=[{self.fit_min_amplitude:.3f}, {self.fit_max_amplitude:.3f}], "
            + f"sigma=[{self.min_sigma:.3f}, {self.max_sigma:.3f}], "
            + f"max_fills={self.max_fills}, "
            + f"cooldown={self.fill_cooldown_sec:.3f}s, "
            + f"min_distance={self.min_distance_between_fills:.3f}m, "
            + "min_event_center_distance="
            + f"{self.min_event_center_distance_between_fills:.3f}m, "
            + f"center_source={self.center_source}, "
            + "max_fit_center_distance_from_event="
            + f"{self.max_fit_center_distance_from_event:.3f}m"
        )

    def _parameter_float(self, name):
        return float(self.get_parameter(name).value)

    @staticmethod
    def _stamp_sec(stamp):
        return float(stamp.sec) + float(stamp.nanosec) * 1e-9

    def pose_cb(self, msg: Odometry):
        """Buffer an absolute-ROS-stamped pose for robust synchronization."""

        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        quaternion = np.array(
            [orientation.x, orientation.y, orientation.z, orientation.w],
            dtype=np.float64,
        )
        norm = float(np.linalg.norm(quaternion))
        valid = bool(
            np.all(np.isfinite(quaternion))
            and norm > 1e-9
            and np.all(np.isfinite([position.x, position.y]))
        )
        if valid:
            quaternion = quaternion / norm
            x_value, y_value, z_value, w_value = quaternion
            yaw = math.atan2(
                2.0 * (w_value * z_value + x_value * y_value),
                1.0 - 2.0 * (y_value ** 2 + z_value ** 2),
            )
            x_position = float(position.x)
            y_position = float(position.y)
        else:
            yaw = float("nan")
            x_position = float("nan")
            y_position = float("nan")
        self.pose_snapshots.append(
            PoseSnapshot(
                self._stamp_sec(msg.header.stamp),
                x_position,
                y_position,
                yaw,
                valid,
            )
        )

    def algorithm_state_cb(self, msg: AlgorithmState):
        """Cache the most recent valid robust controller mode."""

        if msg.state_valid and int(msg.state) > 0:
            self.latest_algorithm_state = msg
        else:
            self.latest_algorithm_state = None

    def source_cost_cb(self, msg: CostBreakdown):
        """Buffer the configured raw minimization-cost channel."""

        index = self.estimation_channel_index
        raw_cost = np.asarray(msg.raw_cost, dtype=np.float64)
        valid_cost = bool(
            msg.raw_cost_valid
            and int(msg.channel_count) == raw_cost.size
            and 0 <= index < raw_cost.size
            and np.isfinite(raw_cost[index])
        )
        raw_sensor = np.asarray(msg.raw_sensor_value, dtype=np.float64)
        raw_sensor_valid = bool(
            msg.raw_sensor_valid
            and 0 <= index < raw_sensor.size
            and np.isfinite(raw_sensor[index])
        )
        source_score = np.asarray(msg.source_score, dtype=np.float64)
        source_score_valid = bool(
            msg.source_score_valid
            and 0 <= index < source_score.size
            and np.isfinite(source_score[index])
        )
        self.cost_snapshots.append(
            CostSnapshot(
                stamp_sec=self._stamp_sec(msg.stamp),
                raw_sensor_value=(
                    float(raw_sensor[index]) if raw_sensor_valid else float("nan")
                ),
                raw_sensor_valid=raw_sensor_valid,
                raw_cost=float(raw_cost[index]) if valid_cost else float("nan"),
                source_score=(
                    float(source_score[index])
                    if source_score_valid
                    else float("nan")
                ),
                source_score_valid=source_score_valid,
                algorithm_state=(
                    int(self.latest_algorithm_state.state)
                    if self.latest_algorithm_state is not None
                    else 0
                ),
                algorithm_state_valid=self.latest_algorithm_state is not None,
            )
        )

    def _robust_trigger_cb(self, msg):
        """Freeze, estimate, design, associate, and atomically commit a fill."""

        request_started_wall_sec = time.monotonic()
        request_timestamp = float(msg.timestamp)
        redesign_fill_id = robust_fill_redesign_target(msg.header)
        request_ros_time = self.get_clock().now().nanoseconds * 1e-9
        pose_snapshots = tuple(self.pose_snapshots)
        cost_snapshots = tuple(self.cost_snapshots)
        lower_bound = max(
            request_ros_time - self.estimator_config.estimation_window_sec,
            request_ros_time - self.estimator_config.maximum_sample_age_sec,
        )
        tolerance = self.estimator_config.sample_sync_tolerance_sec
        candidate_poses = tuple(
            pose for pose in pose_snapshots
            if (
                math.isfinite(float(pose.stamp_sec))
                and lower_bound - tolerance
                <= float(pose.stamp_sec)
                <= request_ros_time + tolerance
            )
        )
        candidate_costs = tuple(
            cost for cost in cost_snapshots
            if (
                math.isfinite(float(cost.stamp_sec))
                and lower_bound
                <= float(cost.stamp_sec)
                <= request_ros_time
            )
        )
        self.robust_request_diagnostics = {
            'request_started_wall_sec': request_started_wall_sec,
            'pose_snapshot_count': float(len(pose_snapshots)),
            'cost_snapshot_count': float(len(cost_snapshots)),
            'candidate_pose_count': float(len(candidate_poses)),
            'candidate_cost_count': float(len(candidate_costs)),
        }
        synchronized, unmatched = synchronize_samples(
            candidate_poses,
            candidate_costs,
            tolerance,
        )
        window = freeze_sample_window(
            synchronized,
            request_ros_time,
            self.estimator_config,
        )
        if (
            redesign_fill_id is not None
            and self.reuse_retained_samples_on_redesign
        ):
            retained_window = retained_redesign_window(
                self.fill_registry,
                redesign_fill_id
            )
            if retained_window is None:
                self._publish_robust_failure(
                    AlgorithmEvent.EVENT_FILL_REJECTED,
                    33,
                    'targeted redesign fill is absent or has no active replacement',
                    request_timestamp,
                    window,
                    unmatched,
                )
                return
            window = retained_window
            unmatched = 0
            self.robust_request_diagnostics[
                'retained_redesign_sample_reuse'
            ] = 1.0
            if window.valid_count < self.estimator_config.minimum_valid_samples:
                self._publish_robust_failure(
                    AlgorithmEvent.EVENT_FILL_REJECTED,
                    31,
                    'retained redesign sample history is below the fixed minimum',
                    request_timestamp,
                    window,
                    unmatched,
                )
                return
        if window.valid_count < self.estimator_config.minimum_valid_samples:
            self._publish_robust_failure(
                AlgorithmEvent.EVENT_FILL_REJECTED,
                30,
                "insufficient valid synchronized samples",
                request_timestamp,
                window,
                unmatched,
            )
            return
        try:
            candidate_fill_evidence = (
                decode_candidate_informed_fill_payload(
                    msg.header,
                    msg.data,
                )
            )
        except (TypeError, ValueError) as exc:
            self._publish_robust_failure(
                AlgorithmEvent.EVENT_FILL_REJECTED,
                35,
                "candidate-informed fill request invalid: " + str(exc),
                request_timestamp,
                window,
                unmatched,
            )
            return
        if redesign_fill_id is None:
            if (
                self.candidate_informed_fill_enabled
                and candidate_fill_evidence is None
            ):
                self._publish_robust_failure(
                    AlgorithmEvent.EVENT_FILL_REJECTED,
                    35,
                    "candidate-informed fill evidence is required",
                    request_timestamp,
                    window,
                    unmatched,
                )
                return
            if (
                not self.candidate_informed_fill_enabled
                and candidate_fill_evidence is not None
            ):
                self._publish_robust_failure(
                    AlgorithmEvent.EVENT_FILL_REJECTED,
                    35,
                    "candidate-informed fill evidence is disabled",
                    request_timestamp,
                    window,
                    unmatched,
                )
                return
        amplitude_floor = None
        if candidate_fill_evidence is not None:
            amplitude_floor = candidate_amplitude_floor(
                candidate_fill_evidence.lower,
                self.candidate_informed_fill_amplitude_scale,
                self.design_config.amplitude_max,
            )
            self.robust_request_diagnostics.update({
                "candidate_fill_raw_cost_estimate": (
                    candidate_fill_evidence.estimate
                ),
                "candidate_fill_raw_cost_mad": candidate_fill_evidence.mad,
                "candidate_fill_raw_cost_uncertainty": (
                    candidate_fill_evidence.uncertainty
                ),
                "candidate_fill_raw_cost_lower": (
                    candidate_fill_evidence.lower
                ),
                "candidate_fill_rotation_count": float(
                    candidate_fill_evidence.rotation_count
                ),
                "candidate_fill_amplitude_scale": (
                    self.candidate_informed_fill_amplitude_scale
                ),
                "candidate_fill_requested_amplitude_floor": (
                    amplitude_floor.requested
                ),
                "candidate_fill_applied_amplitude_floor": (
                    amplitude_floor.applied
                ),
                "candidate_fill_amplitude_floor_capped": (
                    1.0 if amplitude_floor.capped else 0.0
                ),
            })
        try:
            candidate_estimate = estimate_basin(
                window.samples, self.estimator_config
            )
            candidate_geometry = initial_fill_geometry(
                candidate_estimate,
                self.design_config,
                minimum_amplitude=(
                    amplitude_floor.applied
                    if amplitude_floor is not None
                    else 0.0
                ),
            )
            if redesign_fill_id is None:
                association = self.fill_registry.associate(
                    candidate_estimate.center,
                    candidate_geometry.sigma_major,
                )
            else:
                association = self.fill_registry.associate_target(
                    redesign_fill_id,
                    candidate_estimate.center,
                    candidate_geometry.sigma_major,
                )
                if association is None:
                    self._publish_robust_failure(
                        AlgorithmEvent.EVENT_FILL_REJECTED,
                        33,
                        "targeted redesign fill is absent or has no active replacement",
                        request_timestamp,
                        window,
                        unmatched,
                    )
                    return
                if not association.merge:
                    self._publish_robust_failure(
                        AlgorithmEvent.EVENT_FILL_REJECTED,
                        34,
                        "targeted redesign estimate failed active-cluster overlap",
                        request_timestamp,
                        window,
                        unmatched,
                    )
                    return
            if (
                redesign_fill_id is None
                and not association.merge
                and self.max_fills > 0
                and self.fill_registry.active_count >= self.max_fills
            ):
                self._publish_robust_failure(
                    AlgorithmEvent.EVENT_FILL_REJECTED,
                    15,
                    "maximum active fill-cluster count reached",
                    request_timestamp,
                    window,
                    unmatched,
                )
                return

            samples = window.samples
            estimate = candidate_estimate
            if association.merge:
                samples = self.fill_registry.combined_samples(
                    association.cluster_id, samples
                )
                estimate = estimate_basin(samples, self.estimator_config)
            design = design_fill(
                estimate,
                self.design_config,
                minimum_valid_samples=self.estimator_config.minimum_valid_samples,
                condition_limit=(
                    self.estimator_config.quadratic_condition_number_max
                ),
                minimum_amplitude=(
                    amplitude_floor.applied
                    if amplitude_floor is not None
                    else 0.0
                ),
            )
        except (ValueError, np.linalg.LinAlgError) as exc:
            self._publish_robust_failure(
                AlgorithmEvent.EVENT_FILL_REJECTED,
                31,
                f"robust estimator failed: {exc}",
                request_timestamp,
                window,
                unmatched,
            )
            return

        if design.design_escalations > 0:
            self._publish_robust_design_event(
                AlgorithmEvent.EVENT_FILL_DESIGN_ESCALATED,
                "adaptive fill design escalated",
                request_timestamp,
                estimate,
                design,
                window,
                unmatched,
                association,
            )
        if not design.success:
            self._publish_robust_design_event(
                AlgorithmEvent.EVENT_FILL_DESIGN_FAILED,
                "residual fitted interior minimum remains after bounded escalation",
                request_timestamp,
                estimate,
                design,
                window,
                unmatched,
                association,
                reason_code=32,
            )
            return

        quadratic = estimate.quadratic
        values = {
            "source_timestamp": request_timestamp,
            "center": np.array(design.geometry.center, copy=True),
            "amplitude": design.geometry.amplitude,
            "covariance": np.array(design.geometry.covariance, copy=True),
            "sigma_major": design.geometry.sigma_major,
            "sigma_minor": design.geometry.sigma_minor,
            "orientation": design.geometry.orientation,
            "support_radius": design.geometry.support_radius,
            "exit_radius": design.geometry.exit_radius,
            "confidence": design.confidence,
            "sample_count": estimate.sample_count,
            "fit_residual": quadratic.residual_rms,
            "fit_condition_number": (
                quadratic.condition_number
                if math.isfinite(quadratic.condition_number)
                else float("nan")
            ),
            "fit_condition_number_valid": math.isfinite(
                quadratic.condition_number
            ),
            "design_escalations": design.design_escalations,
        }
        if association.merge:
            old, active = self.fill_registry.commit_revision(
                association.cluster_id, values, samples
            )
            self._publish_robust_fill(old)
            self._publish_event(
                AlgorithmEvent.EVENT_FILL_SUPERSEDED,
                "fill revision superseded",
                old.source_timestamp,
                ["cluster_id", "revision", "superseded_fill_id", "new_fill_id"],
                [
                    float(old.cluster_id),
                    float(old.revision),
                    float(old.fill_id),
                    float(active.fill_id),
                ],
                fill_id=old.fill_id,
            )
        else:
            old, active = self.fill_registry.commit_new(values, samples)
        self._publish_robust_fill(active)
        self._publish_compatibility_fill(active)
        self._publish_robust_design_event(
            (
                AlgorithmEvent.EVENT_FILL_MERGED
                if old is not None
                else AlgorithmEvent.EVENT_FILL_CREATED
            ),
            "merged basin fill revision" if old is not None else "robust basin fill created",
            request_timestamp,
            estimate,
            design,
            window,
            unmatched,
            association,
            fill_id=active.fill_id,
            cluster_id=active.cluster_id,
            revision=active.revision,
            superseded_fill_id=0 if old is None else old.fill_id,
        )
        if design.confidence < self.design_config.low_confidence_threshold:
            self._publish_robust_design_event(
                AlgorithmEvent.EVENT_FILL_LOW_CONFIDENCE,
                "accepted fill is below the configured confidence threshold",
                request_timestamp,
                estimate,
                design,
                window,
                unmatched,
                association,
                fill_id=active.fill_id,
                cluster_id=active.cluster_id,
                revision=active.revision,
            )
        self.fill_count = self.fill_registry.active_count
        self.has_filled = self.fill_count > 0
        self.last_fill_time = request_timestamp
        self.fill_centers = [
            np.array(cluster.active_fill.center, copy=True)
            for cluster in self.fill_registry.active_clusters
        ]

    def _publish_robust_fill(self, version):
        """Publish every field of one immutable robust lifecycle record."""

        msg = GaussianFillMessage()
        msg.stamp = self.get_clock().now().to_msg()
        msg.source_timestamp = float(version.source_timestamp)
        msg.source_timestamp_valid = math.isfinite(version.source_timestamp)
        msg.frame_id = "odom"
        msg.fill_id = int(version.fill_id)
        msg.cluster_id = int(version.cluster_id)
        msg.revision = int(version.revision)
        msg.center_x = float(version.center[0])
        msg.center_y = float(version.center[1])
        msg.amplitude = float(version.amplitude)
        msg.covariance_xx = float(version.covariance[0, 0])
        msg.covariance_xy = float(version.covariance[0, 1])
        msg.covariance_yy = float(version.covariance[1, 1])
        msg.sigma_major = float(version.sigma_major)
        msg.sigma_minor = float(version.sigma_minor)
        msg.orientation = float(version.orientation)
        msg.support_radius = float(version.support_radius)
        msg.exit_radius = float(version.exit_radius)
        msg.confidence = float(version.confidence)
        msg.sample_count = int(version.sample_count)
        msg.fit_residual = float(version.fit_residual)
        msg.fit_condition_number = float(version.fit_condition_number)
        msg.design_escalations = int(version.design_escalations)
        msg.covariance_valid = True
        msg.principal_widths_valid = True
        msg.support_radius_valid = True
        msg.exit_radius_valid = True
        msg.confidence_valid = True
        msg.sample_count_valid = True
        msg.fit_residual_valid = math.isfinite(version.fit_residual)
        msg.fit_condition_number_valid = version.fit_condition_number_valid
        msg.design_escalations_valid = True
        msg.active = bool(version.active)
        msg.superseded = bool(version.superseded)
        self.gaussian_fill_diagnostics_publisher.publish(msg)

    def _publish_compatibility_fill(self, version):
        out = StampedFloat64MultiArray()
        out.header = "GaussianFill2D"
        out.timestamp = float(version.source_timestamp)
        out.data = [
            float(version.amplitude),
            float(version.center[0]),
            float(version.center[1]),
            float(version.sigma_major),
        ]
        self.pub.publish(out)

    def _robust_event_values(
        self,
        estimate,
        design,
        window,
        unmatched,
        association,
        cluster_id=0,
        revision=0,
        superseded_fill_id=0,
    ):
        covariance = design.geometry.covariance
        quadratic = estimate.quadratic
        maximum_curvature = float(
            np.max(np.linalg.eigvalsh(quadratic.positive_hessian))
        )
        names = [
            "input_sample_count",
            "valid_sample_count",
            "rejected_unmatched",
        ]
        values = [float(window.input_count), float(window.valid_count), float(unmatched)]
        for name in sorted(window.rejected):
            names.append(f"rejected_{name}")
            values.append(float(window.rejected[name]))
        diagnostics = {
            **self._request_diagnostic_values(),
            "center_x_m": estimate.center[0],
            "center_y_m": estimate.center[1],
            "covariance_xx_m2": covariance[0, 0],
            "covariance_xy_m2": covariance[0, 1],
            "covariance_yy_m2": covariance[1, 1],
            "sigma_major_m": design.geometry.sigma_major,
            "sigma_minor_m": design.geometry.sigma_minor,
            "orientation_rad": design.geometry.orientation,
            "amplitude_cost_units": design.geometry.amplitude,
            "support_radius_m": design.geometry.support_radius,
            "exit_radius_m": design.geometry.exit_radius,
            "basin_depth_cost_units": estimate.depth,
            "maximum_curvature_cost_per_m2": maximum_curvature,
            "fit_valid": float(quadratic.valid),
            "fit_residual_rms": quadratic.residual_rms,
            "fit_condition_number": (
                quadratic.condition_number
                if math.isfinite(quadratic.condition_number)
                else 0.0
            ),
            "residual_minima_count": design.residual_minima_count,
            "design_escalations": design.design_escalations,
            "amplitude_steps": design.amplitude_steps,
            "width_steps": design.width_steps,
            "confidence": design.confidence,
            "association_probability": association.probability,
            "cluster_id": cluster_id,
            "revision": revision,
            "superseded_fill_id": superseded_fill_id,
        }
        for index, component in enumerate(design.confidence_components):
            diagnostics[f"confidence_component_{index + 1}"] = component
        names.extend(diagnostics)
        values.extend(float(value) for value in diagnostics.values())
        return names, values

    def _request_diagnostic_values(self):
        """Return finite bounded-computation diagnostics for one fill request."""
        if self.robust_request_diagnostics is None:
            return {}
        diagnostics = {
            name: value
            for name, value in self.robust_request_diagnostics.items()
            if name != 'request_started_wall_sec'
        }
        started = self.robust_request_diagnostics['request_started_wall_sec']
        diagnostics['design_duration_wall_sec'] = max(
            0.0, time.monotonic() - started
        )
        return diagnostics

    def _publish_robust_design_event(
        self,
        event_type,
        detail,
        source_timestamp,
        estimate,
        design,
        window,
        unmatched,
        association,
        reason_code=0,
        fill_id=None,
        cluster_id=0,
        revision=0,
        superseded_fill_id=0,
    ):
        names, values = self._robust_event_values(
            estimate,
            design,
            window,
            unmatched,
            association,
            cluster_id,
            revision,
            superseded_fill_id,
        )
        self._publish_event(
            event_type,
            detail,
            source_timestamp,
            names,
            values,
            reason_code=reason_code,
            fill_id=fill_id,
        )

    def _publish_robust_failure(
        self, event_type, reason_code, detail, source_timestamp, window, unmatched
    ):
        names = ["input_sample_count", "valid_sample_count", "rejected_unmatched"]
        values = [float(window.input_count), float(window.valid_count), float(unmatched)]
        for name in sorted(window.rejected):
            names.append(f"rejected_{name}")
            values.append(float(window.rejected[name]))
        for name, value in self._request_diagnostic_values().items():
            names.append(name)
            values.append(float(value))
        self._publish_event(
            event_type,
            detail,
            source_timestamp,
            names,
            values,
            reason_code=reason_code,
        )

    def _normalize_policy(self, policy: str) -> str:
        policy = policy.strip().lower()

        aliases = {
            "off": "none",
            "false": "none",
            "disabled": "none",
            "one_shot": "conditional_gaussian_fill",
            "single": "conditional_gaussian_fill",
            "gaussian_fill": "conditional_gaussian_fill",
            "conditional": "conditional_gaussian_fill",
            "multi": "multi_gaussian_fill",
        }

        policy = aliases.get(policy, policy)

        valid = {
            "none",
            "conditional_gaussian_fill",
            "multi_gaussian_fill",
        }

        if policy not in valid:
            self.get_logger().warn(
                f"Unknown escape_policy '{policy}'. "
                "Falling back to conditional_gaussian_fill."
            )
            return "conditional_gaussian_fill"

        return policy

    def _normalize_center_source(self, source: str) -> str:
        source = source.strip().lower()

        aliases = {
            "event": "event_mean",
            "mean": "event_mean",
            "mean_recent": "event_mean",
            "convergence_event": "event_mean",
            "convergence_mean": "event_mean",
            "history_fit": "fit",
            "fitted": "fit",
            "clamp": "fit_clamped",
            "clamped": "fit_clamped",
        }

        source = aliases.get(source, source)

        valid = {
            "event_mean",
            "fit",
            "fit_clamped",
        }

        if source not in valid:
            self.get_logger().warn(
                f"Unknown center_source '{source}'. Falling back to event_mean."
            )
            return "event_mean"

        return source

    def buffer_cb(self, msg: StampedFloat64MultiArray):
        data = np.array(msg.data, dtype=np.float64)

        # Expect flattened [x0,y0,x1,y1,...]
        if data.size < 2 or (data.size % 2) != 0:
            return

        xy = data.reshape(-1, 2)

        if not np.all(np.isfinite(xy)):
            return

        self.buf_xy = xy

    def cost_history_cb(self, msg: Float64MultiArray):
        data = np.array(msg.data, dtype=np.float64)

        if data.size == 0:
            return

        if not np.all(np.isfinite(data)):
            return

        mean_cost = float(np.mean(data))
        self.pde_cost_mean = mean_cost
        self.buf_cost = data

    def trigger_cb(self, msg: StampedFloat64MultiArray):
        event_time = float(msg.timestamp)
        self.current_event_timestamp = event_time

        if (
            self.enable_observability
            and not self.observability_configuration_published
        ):
            self._publish_configuration_event()
            self.observability_configuration_published = True

        if self.escape_policy == "none":
            self._publish_rejection(13, "fill policy is disabled")
            return

        if self.max_fills == 0:
            self._publish_rejection(14, "maximum fill count is zero")
            return

        if self.robust_profile:
            self._robust_trigger_cb(msg)
            return

        if self.A <= 0.0:
            detail = "Skipping fill: gaussian fill amplitude is <= 0.0."
            self.get_logger().info(detail)
            self._publish_rejection(1, detail)
            return

        if self.max_fills > 0 and self.fill_count >= self.max_fills:
            self._publish_rejection(15, "maximum fill count reached")
            return

        if (
            self.last_fill_time is not None
            and (event_time - self.last_fill_time) < self.fill_cooldown_sec
        ):
            remaining = self.fill_cooldown_sec - (event_time - self.last_fill_time)
            detail = f"Skipping fill: cooldown active for {remaining:.3f}s more."
            self.get_logger().info(detail)
            self._publish_rejection(12, detail)
            return

        event_center = self._extract_event_center(msg)

        fill = self._fit_fill_to_history(event_center)

        if fill is None:
            return

        (
            A,
            fit_mu,
            sigma,
            fitted_A,
            sample_count,
            fit_residual,
            fit_condition_number,
            fit_condition_number_valid,
        ) = fill
        mu = self._select_fill_center(fit_mu, event_center)

        if mu is None:
            return

        basin_center = event_center if event_center is not None else mu

        if self._too_close_to_existing_event_center(basin_center):
            detail = (
                "Skipping fill: convergence-event center "
                + f"({basin_center[0]:.3f},{basin_center[1]:.3f}) is within "
                + f"{self.min_event_center_distance_between_fills:.3f}m "
                + "of an existing filled basin."
            )
            self.get_logger().info(detail)
            self._publish_rejection(10, detail)
            return

        if self._too_close_to_existing_fill(mu):
            detail = (
                "Skipping fill: candidate center "
                + f"({mu[0]:.3f},{mu[1]:.3f}) is within "
                + f"{self.min_distance_between_fills:.3f}m of an existing fill."
            )
            self.get_logger().info(detail)
            self._publish_rejection(11, detail)
            return

        # Publish fill: [A, mu_x, mu_y, sigma]
        out = StampedFloat64MultiArray()
        out.header = "GaussianFill2D"
        out.timestamp = event_time
        out.data = [
            float(A),
            float(mu[0]),
            float(mu[1]),
            float(sigma),
        ]

        if not self.robust_profile:
            self.pub.publish(out)

        fill_id = self.fill_count + 1
        if self.enable_observability:
            self._publish_fill_diagnostics(
                fill_id,
                event_time,
                A,
                mu,
                sigma,
                sample_count,
                fit_residual,
                fit_condition_number,
                fit_condition_number_valid,
            )
            event_values = [
                float(mu[0]),
                float(mu[1]),
                float(A),
                float(sigma),
                float(fitted_A),
                float(sample_count),
                float(fit_residual),
            ]
            event_names = [
                "center_x_m",
                "center_y_m",
                "amplitude_cost_units",
                "sigma_m",
                "fitted_amplitude_cost_units",
                "sample_count",
                "fit_residual_rms",
            ]
            if fit_condition_number_valid:
                event_names.append("fit_condition_number")
                event_values.append(float(fit_condition_number))
            self._publish_event(
                AlgorithmEvent.EVENT_FILL_CREATED,
                "Gaussian fill created",
                event_time,
                event_names,
                event_values,
                fill_id=fill_id,
            )

        if self.robust_profile:
            self.pub.publish(out)

        self.fill_count += 1
        self.has_filled = self.fill_count > 0
        self.last_fill_time = event_time
        self.fill_centers.append(mu)
        self.event_centers.append(basin_center)

        self.get_logger().info(
            f"Published fill #{self.fill_count}: "
            + f"A={A:.3f}, "
            + f"fitted_A={fitted_A:.3f}, "
            + f"cost_mean={self.pde_cost_mean:.3f}, "
            + f"mu=({mu[0]:.3f},{mu[1]:.3f}), "
            + f"sigma={sigma:.3f}, "
            + f"event_center=({basin_center[0]:.3f},{basin_center[1]:.3f}), "
            + f"center_source={self.center_source}"
        )

    def _extract_event_center(self, msg: StampedFloat64MultiArray):
        data = np.array(msg.data, dtype=np.float64)

        # convergence_detector_node publishes:
        # [metric, r_val, decay, mean_recent_x, mean_recent_y, ...]
        if data.size < 5:
            self.get_logger().warn(
                "Convergence event did not include mean_recent center; "
                "falling back to fitted center."
            )
            return None

        center = data[3:5]

        if not np.all(np.isfinite(center)):
            self.get_logger().warn(
                "Convergence event center was non-finite; "
                "falling back to fitted center."
            )
            return None

        return center.astype(np.float64)

    def _select_fill_center(self, fit_mu, event_center):
        if event_center is None:
            return fit_mu

        drift = float(np.linalg.norm(fit_mu - event_center))

        if (
            self.max_fit_center_distance_from_event > 0.0
            and drift > self.max_fit_center_distance_from_event
        ):
            if self.center_source == "fit":
                detail = (
                    "Skipping fill: fitted center drifted "
                    + f"{drift:.3f}m from convergence-event center "
                    + f"(limit {self.max_fit_center_distance_from_event:.3f}m)."
                )
                self.get_logger().info(detail)
                self._publish_rejection(9, detail)
                return None

            if self.center_source == "fit_clamped":
                direction = fit_mu - event_center
                norm = float(np.linalg.norm(direction))
                if norm <= 1e-12:
                    return event_center

                clamped = (
                    event_center
                    + direction / norm * self.max_fit_center_distance_from_event
                )
                self.get_logger().info(
                    "Clamped fitted center from "
                    + f"({fit_mu[0]:.3f},{fit_mu[1]:.3f}) to "
                    + f"({clamped[0]:.3f},{clamped[1]:.3f}); "
                    + f"event_center=({event_center[0]:.3f},{event_center[1]:.3f})"
                )
                return clamped

            self.get_logger().info(
                "Using convergence-event center because fitted center drifted "
                + f"{drift:.3f}m from the event mean."
            )

        if self.center_source == "fit":
            return fit_mu

        if self.center_source == "fit_clamped":
            return fit_mu

        return event_center

    def _gaussian_model(self, params, xy):
        """A * exp(-||xy-mu||^2 / v) + c, using v = 2*sigma^2."""
        A, mu_x, mu_y, v, c = params
        v = max(float(v), 1e-9)
        dx = xy[:, 0] - mu_x
        dy = xy[:, 1] - mu_y
        r2 = dx * dx + dy * dy
        return A * np.exp(-r2 / v) + c

    def _fit_fill_to_history(self, event_center=None):
        if self.buf_xy is None or self.buf_xy.shape[0] < self.min_points:
            detail = (
                f"No sufficient 2D history for Gaussian fit "
                f"(have {0 if self.buf_xy is None else self.buf_xy.shape[0]} points)."
            )
            self.get_logger().warn(detail)
            self._publish_rejection(2, detail)
            return None

        if self.buf_cost is None or self.buf_cost.size < self.min_points:
            detail = (
                f"No sufficient cost history for Gaussian fit "
                f"(have {0 if self.buf_cost is None else self.buf_cost.size} points)."
            )
            self.get_logger().warn(detail)
            self._publish_rejection(3, detail)
            return None

        # Index 0 is freshest in PDE buffer
        N = min(self.buf_xy.shape[0], self.buf_cost.size)

        n_use = max(
            self.min_points,
            int(self.use_recent_fraction * N)
        )

        n_use = min(N, n_use)

        xy_use = self.buf_xy[:n_use, :]
        cost_use = self.buf_cost[:n_use]

        if not np.all(np.isfinite(xy_use)) or not np.all(np.isfinite(cost_use)):
            detail = "Non-finite history found during Gaussian fit."
            self.get_logger().warn(detail)
            self._publish_rejection(4, detail)
            return None

        # Prevent ill-conditioned fits when the recent trajectory has collapsed
        # to a single point. This mirrors the pasted script's static-data guard.
        if np.max(np.std(xy_use, axis=0)) < 1e-4:
            detail = "Position history variance too low for Gaussian fit."
            self.get_logger().warn(detail)
            self._publish_rejection(5, detail)
            return None

        target_y = -cost_use

        c_guess = float(np.min(target_y))
        c_guess = float(np.clip(c_guess, -self.fit_offset_bound, self.fit_offset_bound))
        A_guess = float(np.max(target_y) - c_guess)
        A_guess = float(np.clip(A_guess, 0.0, self.fit_max_amplitude))
        if event_center is not None:
            mu_guess = event_center
        else:
            mu_guess = np.mean(xy_use, axis=0)

        diffs = xy_use - mu_guess[None, :]
        r2 = np.sum(diffs * diffs, axis=1)
        sigma_guess = float(np.sqrt(max(np.mean(r2), self.min_sigma * self.min_sigma)))
        sigma_guess = float(np.clip(sigma_guess, self.min_sigma, self.max_sigma))
        v_guess = 2.0 * sigma_guess * sigma_guess

        p0 = [
            A_guess,
            float(mu_guess[0]),
            float(mu_guess[1]),
            v_guess,
            c_guess,
        ]

        v_min = max(2.0 * self.min_sigma * self.min_sigma, 1e-6)
        v_max = max(v_min, 2.0 * self.max_sigma * self.max_sigma)
        mu_x_lb = -np.inf
        mu_x_ub = np.inf
        mu_y_lb = -np.inf
        mu_y_ub = np.inf

        if (
            event_center is not None
            and self.max_fit_center_distance_from_event > 0.0
        ):
            center_radius = self.max_fit_center_distance_from_event
            mu_x_lb = float(event_center[0] - center_radius)
            mu_x_ub = float(event_center[0] + center_radius)
            mu_y_lb = float(event_center[1] - center_radius)
            mu_y_ub = float(event_center[1] + center_radius)

        lb = [
            0.0,
            mu_x_lb,
            mu_y_lb,
            v_min,
            -self.fit_offset_bound,
        ]
        ub = [
            self.fit_max_amplitude,
            mu_x_ub,
            mu_y_ub,
            v_max,
            self.fit_offset_bound,
        ]

        def residuals(params):
            return self._gaussian_model(params, xy_use) - target_y

        try:
            res = least_squares(
                residuals,
                p0,
                bounds=(lb, ub),
                method="trf",
                max_nfev=500,
            )
        except Exception as exc:
            detail = f"Gaussian fit failed: {exc}"
            self.get_logger().warn(detail)
            self._publish_rejection(6, detail)
            return None

        if not res.success:
            detail = f"Gaussian fit did not converge: {res.message}"
            self.get_logger().warn(detail)
            self._publish_rejection(7, detail)
            return None

        A, mu_x, mu_y, v, _ = res.x

        if A < self.fit_min_amplitude:
            detail = (
                f"Skipping fill: fitted basin amplitude {A:.3f} "
                f"is below threshold {self.fit_min_amplitude:.3f}."
            )
            self.get_logger().info(detail)
            self._publish_rejection(8, detail)
            return None

        sigma = float(np.sqrt(max(v, 0.0) / 2.0))
        sigma = float(np.clip(sigma, self.min_sigma, self.max_sigma))
        mu = np.array([mu_x, mu_y], dtype=np.float64)

        fit_residual = float("nan")
        fit_condition_number = float("nan")
        fit_condition_number_valid = False
        if self.enable_observability:
            fit_residual = float(np.sqrt(np.mean(np.square(res.fun))))
            try:
                fit_condition_number = float(np.linalg.cond(res.jac))
                fit_condition_number_valid = bool(
                    np.isfinite(fit_condition_number)
                )
            except np.linalg.LinAlgError:
                fit_condition_number = float("nan")

        return (
            self.A,
            mu,
            sigma,
            float(A),
            int(n_use),
            fit_residual,
            fit_condition_number,
            fit_condition_number_valid,
        )

    def _too_close_to_existing_fill(self, mu):
        if self.min_distance_between_fills <= 0.0 or not self.fill_centers:
            return False

        centers = np.array(self.fill_centers, dtype=np.float64)
        dists = np.linalg.norm(centers - mu[None, :], axis=1)

        return bool(np.min(dists) < self.min_distance_between_fills)

    def _too_close_to_existing_event_center(self, event_center):
        if (
            self.min_event_center_distance_between_fills <= 0.0
            or not self.event_centers
        ):
            return False

        centers = np.array(self.event_centers, dtype=np.float64)
        dists = np.linalg.norm(centers - event_center[None, :], axis=1)

        return bool(np.min(dists) < self.min_event_center_distance_between_fills)

    def _publish_fill_diagnostics(
        self,
        fill_id,
        source_timestamp,
        amplitude,
        center,
        sigma,
        sample_count,
        fit_residual,
        fit_condition_number,
        fit_condition_number_valid,
    ):
        """Publish the accepted isotropic fill as an append-only registry record."""

        msg = GaussianFillMessage()
        msg.stamp = self.get_clock().now().to_msg()
        msg.source_timestamp = float(source_timestamp)
        msg.source_timestamp_valid = bool(np.isfinite(source_timestamp))
        msg.frame_id = "odom"
        msg.fill_id = fill_id
        msg.cluster_id = fill_id
        msg.revision = 1
        msg.center_x = float(center[0])
        msg.center_y = float(center[1])
        msg.amplitude = float(amplitude)
        msg.covariance_xx = float(sigma * sigma)
        msg.covariance_xy = 0.0
        msg.covariance_yy = float(sigma * sigma)
        msg.sigma_major = float(sigma)
        msg.sigma_minor = float(sigma)
        msg.orientation = 0.0
        msg.support_radius = float("nan")
        msg.exit_radius = float("nan")
        msg.confidence = float("nan")
        msg.sample_count = sample_count
        msg.fit_residual = float(fit_residual)
        msg.fit_condition_number = float(fit_condition_number)
        msg.design_escalations = 0
        msg.covariance_valid = True
        msg.principal_widths_valid = True
        msg.support_radius_valid = False
        msg.exit_radius_valid = False
        msg.confidence_valid = False
        msg.sample_count_valid = True
        msg.fit_residual_valid = bool(np.isfinite(fit_residual))
        msg.fit_condition_number_valid = fit_condition_number_valid
        msg.design_escalations_valid = False
        msg.active = True
        msg.superseded = False
        self.gaussian_fill_diagnostics_publisher.publish(msg)

    def _publish_configuration_event(self):
        """Publish the effective legacy fill configuration once."""

        if self.robust_profile:
            names = [
                "estimation_channel_index",
                "sample_sync_tolerance_sec",
                "maximum_position_speed_mps",
                "outlier_mad_threshold",
                "maximum_cluster_samples",
                "estimation_window_sec",
                "minimum_valid_samples",
                "maximum_sample_age_sec",
                "mean_shift_iterations",
                "center_tolerance_m",
                "position_kernel_bandwidth_m",
                "cost_temperature_normalized",
                "covariance_eigenvalue_min_m2",
                "covariance_eigenvalue_max_m2",
                "quadratic_ridge_lambda",
                "quadratic_condition_number_max",
                "center_cost_percentile",
                "shoulder_cost_percentile",
                "inner_mahalanobis_radius",
                "minimum_basin_depth",
                "covariance_scale",
                "sigma_floor_m",
                "sigma_ceiling_m",
                "amplitude_depth_scale",
                "amplitude_curvature_scale",
                "amplitude_min",
                "amplitude_max",
                "validation_grid_points_per_axis",
                "validation_support_sigma",
                "maximum_design_escalations",
                "amplitude_escalation_factor",
                "width_escalation_factor",
                "grid_minimum_tolerance",
                "support_sigma",
                "exit_sigma",
                "merge_bandwidth_m",
                "merge_radius_scale",
                "minimum_merge_probability",
                "low_confidence_threshold",
                'reuse_retained_samples_on_redesign',
                "candidate_informed_fill_enabled",
                "candidate_informed_fill_amplitude_scale",
                "max_fills",
            ]
            values = []
            for name in names:
                if name == "max_fills":
                    value = self.max_fills
                else:
                    value = self.get_parameter(name).value
                values.append(float(value))
            self._publish_event(
                AlgorithmEvent.EVENT_CONFIGURATION,
                "robust Gaussian estimator, designer, and registry configuration",
                None,
                names,
                values,
            )
            return

        self._publish_event(
            AlgorithmEvent.EVENT_CONFIGURATION,
            f"Gaussian fill configuration; policy={self.escape_policy}",
            None,
            [
                "amplitude_cost_units",
                "min_sigma_m",
                "max_sigma_m",
                "min_points",
                "max_fills",
                "fill_cooldown_sec",
            ],
            [
                self.A,
                self.min_sigma,
                self.max_sigma,
                float(self.min_points),
                float(self.max_fills),
                self.fill_cooldown_sec,
            ],
        )

    def _publish_rejection(self, reason_code, detail):
        """Publish a typed rejection outcome when observability is enabled."""

        if not self.enable_observability:
            return
        self._publish_event(
            AlgorithmEvent.EVENT_FILL_REJECTED,
            detail,
            self.current_event_timestamp,
            [],
            [],
            reason_code=reason_code,
        )

    def _publish_event(
        self,
        event_type,
        detail,
        source_timestamp,
        value_names,
        values,
        reason_code=0,
        fill_id=None,
    ):
        """Publish a typed fill event with explicit availability metadata."""

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
        event.fill_id = 0 if fill_id is None else fill_id
        event.fill_id_valid = fill_id is not None
        event.reason_code = reason_code
        event.detail = detail
        event.value_names = list(value_names)
        event.values = [float(value) for value in values]
        self.algorithm_event_publisher.publish(event)


def main():
    rclpy.init()
    node = GaussianFill()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
