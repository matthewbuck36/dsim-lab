#!/usr/bin/env python3
import argparse
import math
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter

from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import (
    StampedFloat64MultiArray,
    StampedTransformMultiArray,
)


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

        # ---------------- State ----------------

        # Gaussian terms:
        # list[(A, mu_x, mu_y, sigma)]
        self.terms = []

        # Affine terms:
        # list[{"anchor": np.array([x,y]), "b0": np.array([bx,by]), "t0": float}]
        self.affine_terms = []

        # Latest robot center position.
        self.xy = None

        # Low-pass-filtered direction from odometry, used as fallback.
        self.filtered_dir = np.zeros(2, dtype=np.float64)

        # Latest sensor positions from rotating sensor frame.
        self.sensor_xy = None

        # Latest PDE history positions.
        # Shape: (N, 2), where row 0 is newest.
        self.pde_history_xy = None

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

        self.sub_cost = self.create_subscription(
            StampedFloat64MultiArray,
            args.input_cost_topic,
            self.cost_cb,
            10
        )

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

    def cost_cb(self, msg: StampedFloat64MultiArray):
        """
        Apply Gaussian + affine correction to incoming cost values.
        """
        if self.xy is None and self.sensor_xy is None:
            return

        cost_vals = np.array(msg.data, dtype=np.float64)

        if cost_vals.size == 0:
            return

        # Preferred path: evaluate correction per sensor channel.
        if self.sensor_xy is not None and self.sensor_xy.shape[0] == cost_vals.size:
            biases = np.array(
                [
                    self._total_bias_at_xy(float(x), float(y))
                    for x, y in self.sensor_xy
                ],
                dtype=np.float64
            )

            if self.bias_all:
                cost_out = cost_vals + biases
            else:
                cost_out = cost_vals.copy()
                cost_out[0] = cost_out[0] + biases[0]

        else:
            # Fallback path: evaluate correction at robot center.
            if self.xy is None:
                return

            x, y = float(self.xy[0]), float(self.xy[1])
            bias = self._total_bias_at_xy(x, y)

            if self.bias_all:
                cost_out = cost_vals + bias
            else:
                cost_out = cost_vals.copy()
                cost_out[0] = cost_out[0] + bias

        out = StampedFloat64MultiArray()
        out.header = "Modified Cost 2D"
        out.timestamp = msg.timestamp
        out.data = [float(v) for v in cost_out.tolist()]
        self.pub.publish(out)

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
        if not self.affine_terms:
            return 0.0

        now = self._now_sec()
        total = 0.0
        kept_terms = []

        x_vec = np.array([x, y], dtype=np.float64)

        for term in self.affine_terms:
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
            kept_terms.append(term)

        # Remove expired or negligible affine terms.
        self.affine_terms = kept_terms

        return float(total)

    def _total_bias_at_xy(self, x: float, y: float) -> float:
        """
        Total correction added to original cost.
        """
        return self._gaussian_bias_at_xy(x, y) + self._affine_bias_at_xy(x, y)


def main():
    rclpy.init()
    rclpy.spin(ModifiedCost2D())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
