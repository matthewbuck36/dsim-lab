#!/usr/bin/env python3
import argparse
import math
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter

from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    GaussianFill,
    StampedFloat64MultiArray,
    StampedTransformMultiArray,
)
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES


class ModifiedCost2D(Node):
    """
    Adds Gaussian hole/fill correction and advisor-style affine exploration bias.

    Inputs:
      - input_cost_topic              : StampedFloat64MultiArray
      - input_fill_topic              : StampedFloat64MultiArray [A, mu_x, mu_y, sigma]
      - /odom                         : nav_msgs/Odometry
      - /turtlebot3/sensor_transform_chatter : StampedTransformMultiArray
      - /pde_history                  : StampedFloat64MultiArray [x0,y0,x1,y1,...]

    Output:
      - output_topic                  : StampedFloat64MultiArray

    Modified cost:

        J_mod(x,t) = J(x)
                   + sum_i A_i exp(-||x-mu_i||^2 / (2 sigma_i^2))
                   - sum_k b_k(t)^T (x - anchor_k)

    with:

        b_k(t) = b0_k exp(-affine_decay_rate * (t - t0_k))

    The vector b0_k is estimated from the PDE history:

        b0 direction = normalize(anchor - U_i)

    where U_i is the newest history point outside the local exclusion region
    around the discovered source/minimum.

    PDE history convention:
        U[0] = newest point
        U[i] = older points as i increases
    """

    def __init__(self):
        super().__init__("modified_cost_2d")

        parser = argparse.ArgumentParser(
            description="Add Gaussian and affine exploration bias to cost values."
        )
        parser.add_argument("input_cost_topic", type=str)
        parser.add_argument("input_fill_topic", type=str)
        parser.add_argument("output_topic", type=str)
        parser.add_argument(
            "--input_sensor_transform_topic",
            type=str,
            default="/turtlebot3/sensor_transform_chatter",
        )
        parser.add_argument(
            "--input_odom_topic",
            type=str,
            default="/odom",
        )

        args, _ = parser.parse_known_args()

        # Use Gazebo sim time.
        self.set_parameters([
            rclpy.parameter.Parameter(
                "use_sim_time",
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])

        # ---------------- Parameters ----------------

        # If true, evaluate the correction at each sensor channel position.
        # If false, only modify the first channel.
        self.declare_parameter("bias_all_channels", True)

        # Internal fallback low-pass direction estimator from odometry.
        # Used only when PDE history is unavailable.
        self.declare_parameter("direction_lpf_alpha", 0.90)
        self.declare_parameter("min_direction_step", 1e-4)

        # Affine correction settings.
        self.declare_parameter("enable_affine_bias", True)
        self.declare_parameter("affine_gain", 0.5)
        self.declare_parameter("affine_decay_rate", 0.0000005)
        self.declare_parameter("affine_min_norm", 1e-4)
        self.declare_parameter("affine_max_age", 30.0)

        # Sign convention.
        #
        # Cost contribution:
        #
        #     affine(x,t) = - b(t)^T (x - anchor)
        #
        # Depending on whether your downstream ESC/controller effectively
        # minimizes or maximizes the cost, you may need +1 or -1.
        self.declare_parameter("affine_direction_sign", 1.0)

        # PDE history settings.
        self.declare_parameter("input_pde_history_topic", "/pde_history")
        self.declare_parameter("use_pde_history_for_affine", True)

        # Defines the local loop/source region:
        #
        #     exclusion_radius = history_exclusion_radius_factor * sigma
        #
        # The direction for b0 is chosen from the newest PDE-history point
        # outside this radius.
        self.declare_parameter("history_exclusion_radius_factor", 3.0)

        # Direction modes:
        #
        # "outside_to_anchor":
        #     direction = anchor - outside_history_point
        #
        # "anchor_to_outside":
        #     direction = outside_history_point - anchor
        #
        # Usually start with "outside_to_anchor".
        self.declare_parameter("history_direction_mode", "outside_to_anchor")
        self.declare_parameter("enable_observability", False)
        self.declare_parameter(
            "cost_breakdown_topic", "/gesc_gaussian/cost_breakdown"
        )
        self.declare_parameter(
            "algorithm_state_topic", "/gesc_gaussian/algorithm_state"
        )
        self.declare_parameter(
            "algorithm_event_topic", "/gesc_gaussian/algorithm_events"
        )
        self.declare_parameter("observability_source_mode", "simulation")
        self.declare_parameter("algorithm_profile", "legacy")
        self.declare_parameter("source_cost_topic", "/gesc_gaussian/source_cost")
        self.declare_parameter(
            "gaussian_fill_diagnostics_topic", "/gesc_gaussian/gaussian_fills"
        )

        # Read parameters.
        self.bias_all = bool(self.get_parameter("bias_all_channels").value)

        self.direction_lpf_alpha = float(
            self.get_parameter("direction_lpf_alpha").value
        )
        self.direction_lpf_alpha = float(np.clip(self.direction_lpf_alpha, 0.0, 0.999))

        self.min_direction_step = float(
            self.get_parameter("min_direction_step").value
        )

        self.enable_affine_bias = bool(
            self.get_parameter("enable_affine_bias").value
        )
        self.affine_gain = float(
            self.get_parameter("affine_gain").value
        )
        self.affine_decay_rate = float(
            self.get_parameter("affine_decay_rate").value
        )
        self.affine_min_norm = float(
            self.get_parameter("affine_min_norm").value
        )
        self.affine_max_age = float(
            self.get_parameter("affine_max_age").value
        )
        self.affine_direction_sign = float(
            self.get_parameter("affine_direction_sign").value
        )

        self.input_pde_history_topic = str(
            self.get_parameter("input_pde_history_topic").value
        )
        self.use_pde_history_for_affine = bool(
            self.get_parameter("use_pde_history_for_affine").value
        )
        self.history_exclusion_radius_factor = float(
            self.get_parameter("history_exclusion_radius_factor").value
        )
        self.history_direction_mode = str(
            self.get_parameter("history_direction_mode").value
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
        self.observability_source_mode = self._source_mode(
            self.get_parameter("observability_source_mode").value
        )
        self.observability_configuration_published = False

        # ---------------- State ----------------

        # Gaussian terms:
        # list[(A, mu_x, mu_y, sigma)]
        self.terms = []
        self.robust_terms = {}
        self.robust_cluster_fill_ids = {}

        # Affine terms:
        # list[{"anchor": np.array([x,y]), "b0": np.array([bx,by]), "t0": float}]
        self.affine_terms = []
        self.robust_affine_terms = {}
        self.robust_affine_applied = None

        # Latest robot center position.
        self.xy = None

        # Low-pass-filtered direction from odometry, used as fallback.
        self.filtered_dir = np.zeros(2, dtype=np.float64)

        # Latest sensor positions from rotating sensor frame.
        self.sensor_xy = None

        # Latest PDE history positions.
        # Shape: (N, 2), where row 0 is newest.
        self.pde_history_xy = None
        self.algorithm_state = None

        # ---------------- ROS subscriptions/publication ----------------

        self.sub_odom = self.create_subscription(
            Odometry,
            args.input_odom_topic,
            self.odom_cb,
            10
        )

        self.sub_sensor = self.create_subscription(
            StampedTransformMultiArray,
            args.input_sensor_transform_topic,
            self.sensor_cb,
            10
        )

        self.sub_pde_history = self.create_subscription(
            StampedFloat64MultiArray,
            self.input_pde_history_topic,
            self.pde_history_cb,
            10
        )

        self.sub_cost = None
        self.sub_source_cost = None
        self.sub_algorithm_state = None
        if self.robust_profile:
            self.sub_source_cost = self.create_subscription(
                CostBreakdown,
                str(self.get_parameter("source_cost_topic").value),
                self.source_cost_cb,
                10,
            )
            self.sub_algorithm_state = self.create_subscription(
                AlgorithmState,
                str(self.get_parameter("algorithm_state_topic").value),
                self.algorithm_state_cb,
                10,
            )
        else:
            self.sub_cost = self.create_subscription(
                StampedFloat64MultiArray,
                args.input_cost_topic,
                self.cost_cb,
                10
            )

        if self.robust_profile:
            self.sub_fill = self.create_subscription(
                GaussianFill,
                str(self.get_parameter("gaussian_fill_diagnostics_topic").value),
                self.robust_fill_cb,
                10,
            )
        else:
            self.sub_fill = self.create_subscription(
                StampedFloat64MultiArray,
                args.input_fill_topic,
                self.fill_cb,
                10
            )

        self.pub = self.create_publisher(
            StampedFloat64MultiArray,
            args.output_topic,
            10
        )

        self.cost_breakdown_publisher = None
        self.algorithm_state_publisher = None
        self.algorithm_event_publisher = None
        if self.enable_observability:
            self.cost_breakdown_publisher = self.create_publisher(
                CostBreakdown,
                str(self.get_parameter("cost_breakdown_topic").value),
                10,
            )
            if not self.robust_profile:
                self.algorithm_state_publisher = self.create_publisher(
                    AlgorithmState,
                    str(self.get_parameter("algorithm_state_topic").value),
                    10,
                )
            self.algorithm_event_publisher = self.create_publisher(
                AlgorithmEvent,
                str(self.get_parameter("algorithm_event_topic").value),
                10,
            )

        self.get_logger().info(
            "ModifiedCost2D started with Gaussian correction + PDE-history affine bias."
        )
        self.get_logger().info(
            f"PDE history topic: {self.input_pde_history_topic}, "
            f"use_pde_history_for_affine={self.use_pde_history_for_affine}"
        )

    def _now_sec(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------

    def odom_cb(self, msg: Odometry):
        """
        Track current position and maintain a fallback low-pass-filtered direction.

        This fallback direction is only used if PDE history is unavailable.
        """
        p = msg.pose.pose.position
        new_xy = np.array([p.x, p.y], dtype=np.float64)

        if self.xy is not None:
            step = new_xy - self.xy
            step_norm = float(np.linalg.norm(step))

            if step_norm > self.min_direction_step:
                unit_step = step / step_norm

                alpha = self.direction_lpf_alpha
                self.filtered_dir = (
                    alpha * self.filtered_dir
                    + (1.0 - alpha) * unit_step
                )

                filt_norm = float(np.linalg.norm(self.filtered_dir))
                if filt_norm > 1e-12:
                    self.filtered_dir = self.filtered_dir / filt_norm

        self.xy = new_xy

    def sensor_cb(self, msg: StampedTransformMultiArray):
        """
        Store sensor positions so correction can be evaluated per channel.
        """
        if len(msg.transform_array) == 0:
            return

        xy = []
        for tf in msg.transform_array:
            xy.append([tf.translation.x, tf.translation.y])

        self.sensor_xy = np.array(xy, dtype=np.float64)

    def pde_history_cb(self, msg: StampedFloat64MultiArray):
        """
        Receive PDE history:

            msg.data = [x0,y0,x1,y1,...]

        where:
            [x0,y0] is newest
            [xi,yi] gets older as i increases
        """
        data = np.array(msg.data, dtype=np.float64)

        if data.size < 4:
            return

        if data.size % 2 != 0:
            self.get_logger().warn(
                f"Received PDE history with odd length={data.size}; ignoring."
            )
            return

        hist = data.reshape((-1, 2))

        if not np.all(np.isfinite(hist)):
            self.get_logger().warn("Received non-finite PDE history; ignoring.")
            return

        self.pde_history_xy = hist

    def fill_cb(self, msg: StampedFloat64MultiArray):
        """
        Receive a new Gaussian hole/fill term and create a corresponding
        affine exploration term.

        Expected input:

            [A, mu_x, mu_y, sigma]
        """
        data = list(msg.data)

        if len(data) != 4:
            self.get_logger().warn(
                f"Received fill/bias with len={len(data)}; expected 4: "
                "[A, mu_x, mu_y, sigma]. Ignoring."
            )
            return

        A, mu_x, mu_y, sigma = map(float, data)

        if not np.isfinite([A, mu_x, mu_y, sigma]).all():
            self.get_logger().warn("Received NaN/Inf in fill/bias message. Ignoring.")
            return

        sigma = max(sigma, 1e-6)

        # 1. Add Gaussian correction.
        self.terms.append((A, mu_x, mu_y, sigma))

        self.get_logger().info(
            f"Added Gaussian term: A={A:.3f}, "
            f"mu=({mu_x:.3f},{mu_y:.3f}), sigma={sigma:.3f} "
            f"(total Gaussian terms={len(self.terms)})"
        )

        # 2. Add affine exploration correction.
        if not self.enable_affine_bias:
            return

        direction = None

        if self.use_pde_history_for_affine:
            direction = self._get_direction_from_pde_history(mu_x, mu_y, sigma)

        # Fallback to low-pass odometry direction if PDE history is unavailable.
        if direction is None:
            direction = self._get_direction_from_filtered_odom()

        if direction is None:
            self.get_logger().warn(
                "Cannot create affine term: no valid PDE-history or odom direction."
            )
            return

        b0 = self.affine_direction_sign * self.affine_gain * direction
        anchor = np.array([mu_x, mu_y], dtype=np.float64)
        t0 = self._now_sec()

        self.affine_terms.append({
            "anchor": anchor,
            "b0": b0,
            "t0": t0,
        })

        self.get_logger().info(
            f"Added affine term: "
            f"anchor=({anchor[0]:.3f},{anchor[1]:.3f}), "
            f"direction=({direction[0]:.3f},{direction[1]:.3f}), "
            f"b0=({b0[0]:.3f},{b0[1]:.3f}), "
            f"decay_rate={self.affine_decay_rate:.3f}, "
            f"total affine terms={len(self.affine_terms)}"
        )

    def robust_fill_cb(self, msg: GaussianFill):
        """Apply typed anisotropic fill lifecycle updates without stacking revisions."""

        cluster_id = int(msg.cluster_id)
        fill_id = int(msg.fill_id)
        revision = int(msg.revision)
        if cluster_id <= 0 or fill_id <= 0 or revision <= 0:
            return
        current_fill_id = self.robust_cluster_fill_ids.get(cluster_id)
        current = (
            self.robust_terms.get(current_fill_id)
            if current_fill_id is not None
            else None
        )
        if current is not None:
            if revision < current["revision"]:
                return
            if revision == current["revision"]:
                if (msg.superseded or not msg.active) and fill_id == current_fill_id:
                    del self.robust_terms[current_fill_id]
                    del self.robust_cluster_fill_ids[cluster_id]
                    self.robust_affine_terms.pop(cluster_id, None)
                return

        if msg.superseded or not msg.active:
            if current is not None and fill_id == current_fill_id:
                del self.robust_terms[current_fill_id]
                del self.robust_cluster_fill_ids[cluster_id]
                self.robust_affine_terms.pop(cluster_id, None)
            return

        finite = np.array(
            [
                msg.center_x,
                msg.center_y,
                msg.amplitude,
                msg.covariance_xx,
                msg.covariance_xy,
                msg.covariance_yy,
                msg.sigma_major,
                msg.sigma_minor,
            ],
            dtype=np.float64,
        )
        if (
            not msg.covariance_valid
            or not msg.principal_widths_valid
            or not np.all(np.isfinite(finite))
            or msg.amplitude < 0.0
            or msg.sigma_major <= 0.0
            or msg.sigma_minor <= 0.0
        ):
            return
        covariance = np.array(
            [
                [msg.covariance_xx, msg.covariance_xy],
                [msg.covariance_xy, msg.covariance_yy],
            ],
            dtype=np.float64,
        )
        covariance = 0.5 * (covariance + covariance.T)
        eigenvalues = np.linalg.eigvalsh(covariance)
        if not np.all(np.isfinite(eigenvalues)) or np.min(eigenvalues) <= 0.0:
            return
        try:
            inverse = np.linalg.inv(covariance)
        except np.linalg.LinAlgError:
            return

        if current_fill_id is not None:
            self.robust_terms.pop(current_fill_id, None)
        self.robust_terms[fill_id] = {
            "fill_id": fill_id,
            "cluster_id": cluster_id,
            "revision": revision,
            "amplitude": float(msg.amplitude),
            "center": np.array([msg.center_x, msg.center_y], dtype=np.float64),
            "covariance": covariance,
            "inverse": inverse,
            "sigma_major": float(msg.sigma_major),
        }
        self.robust_cluster_fill_ids[cluster_id] = fill_id
        self._sync_robust_affine()

    def algorithm_state_cb(self, msg: AlgorithmState):
        """Cache robust authorization and bind affine assistance by revision."""

        weights = np.array(
            [msg.sensor_weight, msg.gaussian_weight, msg.affine_weight],
            dtype=np.float64,
        )
        if not msg.state_valid or not msg.weights_valid or not np.all(np.isfinite(weights)):
            self.algorithm_state = None
            self.robust_affine_terms.clear()
            return
        self.algorithm_state = msg
        self._sync_robust_affine()

    def _sync_robust_affine(self):
        """Create exactly one robust affine term from the selected safe direction."""

        state = self.algorithm_state
        authorized_state = bool(
            state is not None
            and state.state
            in (
                AlgorithmState.STATE_ESCAPE_REPULSE,
                AlgorithmState.STATE_ESCAPE_ASSIST,
                AlgorithmState.STATE_SEARCH,
            )
            and float(state.affine_weight) > 0.0
        )
        if (
            not self.robust_profile
            or not self.enable_affine_bias
            or state is None
            or not authorized_state
            or not state.active_escape_fill_id_valid
            or not state.safe_direction_valid
            or not state.safe_direction_revision_valid
            or int(state.safe_direction_revision) <= 0
        ):
            self.robust_affine_terms.clear()
            self.robust_affine_applied = None
            return
        direction = np.array(
            [state.safe_direction_x, state.safe_direction_y], dtype=np.float64
        )
        norm = float(np.linalg.norm(direction))
        if not np.all(np.isfinite(direction)) or norm <= 1e-12:
            self.robust_affine_terms.clear()
            return
        fill_id = int(state.active_escape_fill_id)
        fill = self.robust_terms.get(fill_id)
        if fill is None:
            self.robust_affine_terms.clear()
            return
        cluster_id = int(fill["cluster_id"])
        revision = int(state.safe_direction_revision)
        current = self.robust_affine_terms.get(cluster_id)
        if (
            current is not None
            and current.get("direction_revision") == revision
            and current.get("fill_id") == fill_id
        ):
            self.robust_affine_terms = {cluster_id: current}
            return
        applied_key = (cluster_id, fill_id, revision)
        if self.robust_affine_applied == applied_key:
            self.robust_affine_terms.clear()
            return
        direction = direction / norm
        self.robust_affine_terms = {
            cluster_id: {
                "anchor": np.array(fill["center"], dtype=np.float64, copy=True),
                "b0": self.affine_direction_sign * self.affine_gain * direction,
                "t0": self._now_sec(),
                "direction_revision": revision,
                "fill_id": fill_id,
            }
        }
        self.robust_affine_applied = applied_key

    def source_cost_cb(self, msg: CostBreakdown):
        """Consume synchronized raw cost and source score in robust mode."""

        if (
            not msg.source_timestamp_valid
            or not np.isfinite(msg.source_timestamp)
            or not msg.raw_cost_valid
            or int(msg.channel_count) != len(msg.raw_cost)
        ):
            return
        raw_cost = np.asarray(msg.raw_cost, dtype=np.float64)
        if raw_cost.size == 0 or not np.all(np.isfinite(raw_cost)):
            return
        legacy = StampedFloat64MultiArray()
        legacy.header = "Robust Source Cost"
        legacy.timestamp = float(msg.source_timestamp)
        legacy.data = [float(value) for value in raw_cost]
        self._apply_cost(legacy, msg)

    def cost_cb(self, msg: StampedFloat64MultiArray):
        """
        Apply Gaussian + affine correction to incoming cost values.
        """
        self._apply_cost(msg, None)

    def _apply_cost(self, msg, source_breakdown):
        """Apply legacy or state-weighted cost composition once per sample."""

        if self.xy is None and self.sensor_xy is None:
            return

        if self.robust_profile and self.algorithm_state is None:
            return

        cost_vals = np.array(msg.data, dtype=np.float64)

        if cost_vals.size == 0:
            return

        # Preferred path: evaluate correction per sensor channel.
        if self.sensor_xy is not None and self.sensor_xy.shape[0] == cost_vals.size:
            components = [
                self._bias_components_at_xy(float(x), float(y))
                for x, y in self.sensor_xy
            ]
            gaussian_cost = np.array(
                [component[0] for component in components], dtype=np.float64
            )
            affine_cost = np.array(
                [component[1] for component in components], dtype=np.float64
            )
            biases = np.array(
                [component[2] for component in components], dtype=np.float64
            )

            if self.bias_all:
                cost_out = cost_vals + biases
            else:
                cost_out = cost_vals.copy()
                cost_out[0] = cost_out[0] + biases[0]
                gaussian_cost[1:] = 0.0
                affine_cost[1:] = 0.0

        else:
            # Fallback path: evaluate correction at robot center.
            if self.xy is None:
                return

            x, y = float(self.xy[0]), float(self.xy[1])
            gaussian_bias, affine_bias, bias = self._bias_components_at_xy(x, y)

            if self.bias_all:
                cost_out = cost_vals + bias
                gaussian_cost = np.full(cost_vals.shape, gaussian_bias)
                affine_cost = np.full(cost_vals.shape, affine_bias)
            else:
                cost_out = cost_vals.copy()
                cost_out[0] = cost_out[0] + bias
                gaussian_cost = np.zeros(cost_vals.shape, dtype=np.float64)
                affine_cost = np.zeros(cost_vals.shape, dtype=np.float64)
                gaussian_cost[0] = gaussian_bias
                affine_cost[0] = affine_bias

        if self.robust_profile:
            sensor_weight = float(self.algorithm_state.sensor_weight)
            gaussian_weight = float(self.algorithm_state.gaussian_weight)
            affine_weight = float(self.algorithm_state.affine_weight)
            cost_out = (
                sensor_weight * cost_vals
                + gaussian_weight * gaussian_cost
                + affine_weight * affine_cost
            )

        out = StampedFloat64MultiArray()
        out.header = "Modified Cost 2D"
        out.timestamp = msg.timestamp
        out.data = [float(v) for v in cost_out.tolist()]
        self.pub.publish(out)

        if self.enable_observability:
            self._publish_observability(
                msg,
                cost_vals,
                gaussian_cost,
                affine_cost,
                cost_out,
                source_breakdown,
            )

    # ------------------------------------------------------------
    # Direction estimation
    # ------------------------------------------------------------

    def _get_direction_from_pde_history(
        self,
        mu_x: float,
        mu_y: float,
        sigma: float
    ):
        """
        Estimate b0 direction using PDE position history.

        Choose the newest history point outside the local exclusion radius:

            ||U_i - mu|| > history_exclusion_radius_factor * sigma

        Then construct a direction from that point to the anchor:

            direction = normalize(mu - U_i)

        This estimates the approach direction before the robot entered
        the local loop/source region.
        """
        if self.pde_history_xy is None or self.pde_history_xy.shape[0] < 2:
            return None

        mu = np.array([mu_x, mu_y], dtype=np.float64)
        exclusion_radius = self.history_exclusion_radius_factor * sigma

        # Search newest to oldest.
        # The first point outside the exclusion radius is the estimated
        # pre-loop entry point.
        for i in range(self.pde_history_xy.shape[0]):
            p_hist = self.pde_history_xy[i, :]

            dist = float(np.linalg.norm(p_hist - mu))

            if dist > exclusion_radius:
                if self.history_direction_mode == "outside_to_anchor":
                    direction = mu - p_hist
                elif self.history_direction_mode == "anchor_to_outside":
                    direction = p_hist - mu
                else:
                    self.get_logger().warn(
                        f"Unknown history_direction_mode={self.history_direction_mode}; "
                        "using outside_to_anchor."
                    )
                    direction = mu - p_hist

                norm = float(np.linalg.norm(direction))
                if norm > 1e-9:
                    self.get_logger().info(
                        f"PDE direction selected from history index {i}, "
                        f"dist={dist:.3f}, exclusion_radius={exclusion_radius:.3f}"
                    )
                    return direction / norm

        # If all stored history is inside the exclusion radius, use the oldest point.
        p_oldest = self.pde_history_xy[-1, :]

        if self.history_direction_mode == "outside_to_anchor":
            direction = mu - p_oldest
        else:
            direction = p_oldest - mu

        norm = float(np.linalg.norm(direction))
        if norm > 1e-9:
            self.get_logger().warn(
                "All PDE-history points are inside exclusion radius; "
                "using oldest point as fallback."
            )
            return direction / norm

        return None

    def _get_direction_from_filtered_odom(self):
        """
        Fallback direction based on low-pass-filtered recent odometry.
        """
        dir_norm = float(np.linalg.norm(self.filtered_dir))

        if dir_norm < 1e-9:
            return None

        return self.filtered_dir / dir_norm

    # ------------------------------------------------------------
    # Bias/correction functions
    # ------------------------------------------------------------

    def _gaussian_bias_at_xy(self, x: float, y: float) -> float:
        """
        Compute total Gaussian hole/fill correction at position (x,y).
        """
        if self.robust_profile:
            point = np.array([x, y], dtype=np.float64)
            bias = 0.0
            for term in self.robust_terms.values():
                delta = point - term["center"]
                exponent = -0.5 * float(delta.T @ term["inverse"] @ delta)
                bias += term["amplitude"] * math.exp(exponent)
            return float(bias)

        if not self.terms:
            return 0.0

        bias = 0.0

        for A, mu_x, mu_y, sigma in self.terms:
            dx = x - mu_x
            dy = y - mu_y
            r2 = dx * dx + dy * dy
            bias += A * math.exp(-r2 / (2.0 * sigma * sigma))

        return float(bias)

    def _affine_bias_at_xy(self, x: float, y: float) -> float:
        """
        Compute total decaying affine correction at position (x,y):

            affine(x,t) = - b(t)^T (x - anchor)

        where:

            b(t) = b0 exp(-affine_decay_rate * (t - t0))
        """
        if self.robust_profile:
            terms = list(self.robust_affine_terms.items())
        else:
            terms = list(enumerate(self.affine_terms))
        if not terms:
            return 0.0

        now = self._now_sec()
        total = 0.0
        kept_terms = []

        x_vec = np.array([x, y], dtype=np.float64)

        for key, term in terms:
            anchor = term["anchor"]
            b0 = term["b0"]
            t0 = term["t0"]

            age = max(0.0, now - t0)

            if self.affine_max_age > 0.0 and age > self.affine_max_age:
                continue

            decay = math.exp(-self.affine_decay_rate * age)
            b_t = decay * b0

            if float(np.linalg.norm(b_t)) < self.affine_min_norm:
                continue

            total += -float(np.dot(b_t, x_vec - anchor))
            kept_terms.append((key, term))

        # Remove expired or negligible affine terms.
        if self.robust_profile:
            self.robust_affine_terms = dict(kept_terms)
        else:
            self.affine_terms = [term for _, term in kept_terms]

        return float(total)

    def _total_bias_at_xy(self, x: float, y: float) -> float:
        """
        Total correction added to original cost.
        """
        return self._bias_components_at_xy(x, y)[2]

    def _bias_components_at_xy(self, x: float, y: float):
        """Evaluate each correction exactly once and retain its decomposition."""

        gaussian = self._gaussian_bias_at_xy(x, y)
        affine = self._affine_bias_at_xy(x, y)
        return gaussian, affine, gaussian + affine

    def _publish_observability(
        self,
        source_msg,
        raw_cost,
        gaussian_cost,
        affine_cost,
        augmented_cost,
        source_breakdown=None,
    ):
        """Publish typed cost/state mirrors after the legacy modified cost."""

        stamp = self.get_clock().now().to_msg()
        if not self.observability_configuration_published:
            self._publish_configuration_event(stamp)
            self.observability_configuration_published = True

        raw_values = [float(value) for value in raw_cost.tolist()]
        gaussian_values = [float(value) for value in gaussian_cost.tolist()]
        affine_values = [float(value) for value in affine_cost.tolist()]
        augmented_values = [float(value) for value in augmented_cost.tolist()]
        unavailable = [float("nan")] * len(raw_values)
        if self.robust_profile:
            sensor_weight = float(self.algorithm_state.sensor_weight)
            gaussian_weight = float(self.algorithm_state.gaussian_weight)
            affine_weight = float(self.algorithm_state.affine_weight)
        else:
            sensor_weight = 1.0
            gaussian_weight = 1.0
            affine_weight = 1.0 if self.enable_affine_bias else 0.0
        source_score = unavailable
        source_score_valid = False
        if source_breakdown is not None:
            candidate = [float(value) for value in source_breakdown.source_score]
            if (
                source_breakdown.source_score_valid
                and len(candidate) == len(raw_values)
                and np.all(np.isfinite(candidate))
            ):
                source_score = candidate
                source_score_valid = True

        breakdown = CostBreakdown()
        breakdown.stamp = stamp
        breakdown.source_timestamp = float(source_msg.timestamp)
        breakdown.source_timestamp_valid = bool(
            np.isfinite(source_msg.timestamp)
        )
        breakdown.source_mode = self.observability_source_mode
        breakdown.source_name = "modified_cost_2d"
        breakdown.channel_count = len(raw_values)
        breakdown.raw_sensor_value = unavailable
        breakdown.filtered_sensor_value = unavailable
        breakdown.raw_cost = raw_values
        breakdown.source_score = source_score
        breakdown.gaussian_cost = gaussian_values
        breakdown.affine_cost = affine_values
        breakdown.augmented_cost = augmented_values
        breakdown.sensor_weight = sensor_weight
        breakdown.gaussian_weight = gaussian_weight
        breakdown.affine_weight = affine_weight
        breakdown.raw_sensor_valid = False
        breakdown.filtered_sensor_valid = False
        breakdown.raw_cost_valid = bool(np.all(np.isfinite(raw_cost)))
        breakdown.source_score_valid = source_score_valid
        breakdown.gaussian_cost_valid = bool(
            np.all(np.isfinite(gaussian_cost))
        )
        breakdown.affine_cost_valid = bool(np.all(np.isfinite(affine_cost)))
        breakdown.augmented_cost_valid = bool(
            np.all(np.isfinite(augmented_cost))
        )
        breakdown.weights_valid = True
        self.cost_breakdown_publisher.publish(breakdown)

        if self.algorithm_state_publisher is None:
            return

        state = AlgorithmState()
        state.stamp = stamp
        state.source_timestamp = float(source_msg.timestamp)
        state.source_timestamp_valid = bool(np.isfinite(source_msg.timestamp))
        state.run_id = ""
        state.run_id_valid = False
        state.algorithm_profile = self.algorithm_profile
        state.state = AlgorithmState.STATE_UNAVAILABLE
        state.state_name = "UNAVAILABLE"
        state.state_valid = False
        state.previous_state = AlgorithmState.STATE_UNAVAILABLE
        state.previous_state_name = "UNAVAILABLE"
        state.previous_state_valid = False
        state.transition_reason = ""
        state.transition_reason_valid = False
        state.state_elapsed_sec = float("nan")
        state.state_elapsed_valid = False
        state.active_fill_count = len(self.terms)
        state.active_fill_count_valid = True
        state.active_escape_fill_id = 0
        state.active_escape_fill_id_valid = False
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
        state.sensor_weight = sensor_weight
        state.gaussian_weight = gaussian_weight
        state.affine_weight = affine_weight
        state.weights_valid = True
        state.failsafe = False
        state.failsafe_valid = False
        self.algorithm_state_publisher.publish(state)

    def _publish_configuration_event(self, stamp):
        """Publish the effective profile composition policy once."""

        event = AlgorithmEvent()
        event.stamp = stamp
        event.source_timestamp = float("nan")
        event.source_timestamp_valid = False
        event.event_type = AlgorithmEvent.EVENT_CONFIGURATION
        event.state = AlgorithmState.STATE_UNAVAILABLE
        event.state_name = "UNAVAILABLE"
        event.state_valid = False
        event.fill_id = 0
        event.fill_id_valid = False
        event.reason_code = 0
        event.detail = (
            "state-driven robust weights"
            if self.robust_profile
            else "legacy fixed observational weights"
        )
        if self.robust_profile and self.algorithm_state is not None:
            sensor_weight = float(self.algorithm_state.sensor_weight)
            gaussian_weight = float(self.algorithm_state.gaussian_weight)
            affine_weight = float(self.algorithm_state.affine_weight)
        else:
            sensor_weight = 1.0
            gaussian_weight = 1.0
            affine_weight = 1.0 if self.enable_affine_bias else 0.0
        event.value_names = [
            "sensor_weight",
            "gaussian_weight",
            "affine_weight",
            "bias_all_channels",
        ]
        event.values = [
            sensor_weight,
            gaussian_weight,
            affine_weight,
            1.0 if self.bias_all else 0.0,
        ]
        self.algorithm_event_publisher.publish(event)

    @staticmethod
    def _source_mode(value):
        """Map a platform adapter parameter to the common source enum."""

        normalized = str(value).strip().lower()
        if normalized == "simulation":
            return CostBreakdown.SOURCE_SIMULATION
        if normalized == "physical":
            return CostBreakdown.SOURCE_PHYSICAL
        return CostBreakdown.SOURCE_UNKNOWN


def main():
    rclpy.init()
    node = ModifiedCost2D()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
