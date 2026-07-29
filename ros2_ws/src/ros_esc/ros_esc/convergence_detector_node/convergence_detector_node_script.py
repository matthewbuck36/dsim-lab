#!/usr/bin/env python3
import numpy as np
import rclpy
from rclpy.node import Node
import rclpy.parameter
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    StampedFloat64MultiArray,
)


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


class SearchEpochGate:
    """Track valid typed SEARCH epochs without changing legacy behavior."""

    ENTERED = "entered"
    LEFT = "left"

    def __init__(self, enabled):
        self.enabled = bool(enabled)
        self.active = not self.enabled
        self.run_id = None

    def update(self, state):
        if not self.enabled:
            return None
        valid_search = bool(
            state.state_valid and int(state.state) == AlgorithmState.STATE_SEARCH
        )
        run_id = str(state.run_id) if state.run_id_valid else None
        if valid_search:
            entered = not self.active or run_id != self.run_id
            self.active = True
            self.run_id = run_id
            return self.ENTERED if entered else None
        if self.active:
            self.active = False
            self.run_id = run_id
            return self.LEFT
        self.run_id = run_id
        return None


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

        # Use Gazebo simulation time
        self.set_parameters([
            rclpy.parameter.Parameter(
                "use_sim_time",
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])

        # ---------------------------------------------------------------------
        # Parameters
        # ---------------------------------------------------------------------

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
        self.search_gate = SearchEpochGate(self.state_gating_enabled)

        # ---------------------------------------------------------------------
        # Subscribers
        # ---------------------------------------------------------------------

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

        self.get_logger().info(
            f"ConvergenceDetector: k={self.k}, th={self.th}, b={self.b}, "
            f"N={self.N}, omega={self.omega:.3f}, dt_node={self.dt_node:.6f}, "
            f"min_trigger_time={self.min_time_before_trigger:.2f}s, "
            f"count_start={self.count_start}, "
            f"state_gating={self.state_gating_enabled}, "
            f"minimum_path_length_m={self.minimum_path_length_m:.3f}, "
            f"maximum_path_efficiency={self.maximum_path_efficiency:.3f}"
        )

    def _reset_detection_state(self):
        """Start a fresh detector epoch and convergence counter."""
        self.t0 = None
        self.first_time = None
        self.last_metric = None
        self.count_remaining = self.count_start

    def algorithm_state_cb(self, msg):
        """Reset on every typed SEARCH boundary and disarm outside SEARCH."""
        boundary = self.search_gate.update(msg)
        if boundary in (SearchEpochGate.ENTERED, SearchEpochGate.LEFT):
            self._reset_detection_state()

    def buffer_cb(self, msg: StampedFloat64MultiArray):
        t = float(msg.timestamp)

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
            return

        if data.size % 2 != 0:
            return

        U = data.reshape(-1, 2)

        if not np.all(np.isfinite(U)):
            return

        N = U.shape[0]

        if N < self.k * 3:
            return

        M = N // self.k

        if 3 * M > N or M <= 0:
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

        count_msg = StampedFloat64MultiArray()
        count_msg.header = "CONV_COUNT"
        count_msg.timestamp = t
        count_msg.data = [float(self.count_remaining)]
        self.pub_count.publish(count_msg)

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
            self.convergence_status_publisher.publish(status_msg)

        # ---------------------------------------------------------------------
        # Crossing logic
        # ---------------------------------------------------------------------

        if self.last_metric is None:
            self.last_metric = metric
            return

        crossed = self.last_metric > 0.0 and metric < 0.0
        self.last_metric = metric

        if not crossed:
            return

        # ---------------------------------------------------------------------
        # A convergence candidate was detected.
        # Decrement the counter.
        # ---------------------------------------------------------------------

        self.count_remaining -= 1

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
            out = StampedFloat64MultiArray()
            out.header = "CONVERGED_FILL_READY"
            out.timestamp = t

            out.data = [
                float(metric),
                float(r_val),
                float(decay_term),

                # Recommended fill center estimate:
                float(mean_recent[0]),
                float(mean_recent[1]),

                # Old segment mean, useful for diagnostics:
                float(mean_old[0]),
                float(mean_old[1]),

                # Counter state:
                float(self.count_remaining),
            ]

            self.pub.publish(out)

            self.get_logger().info(
                "CONVERGED_FILL_READY: "
                + f"metric={metric:.6f}, "
                + f"r_mean={r_val:.6f}, "
                + f"decay={decay_term:.6f}, "
                + f"fill_center=({mean_recent[0]:.4f}, {mean_recent[1]:.4f}), "
                + f"t={t:.3f}"
            )

            if self.enable_observability:
                self._publish_event(
                    AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED,
                    "convergence confirmed; fill ready",
                    source_timestamp=t,
                    value_names=[
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

            if self.reset_counter_after_event:
                self.count_remaining = self.count_start

                self.get_logger().info(
                    f"Convergence counter reset to {self.count_start}"
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
