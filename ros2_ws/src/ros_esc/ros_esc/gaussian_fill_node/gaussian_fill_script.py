#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter
from ros_esc_interfaces.msg import StampedFloat64MultiArray


class GaussianFill(Node):
    """
    Adds Gaussian fills at detected trap locations.

    - Reads 2D position history from /pde_history as [x0,y0,x1,y1,...].
    - On /convergence_event (metric crossed), computes (mu_x, mu_y) and sigma.
    - Publishes /cost_bias: [A, mu_x, mu_y, sigma].

    Policies:
      none:
        Ignore convergence events and publish no fills.
      conditional_gaussian_fill:
        Publish fills when convergence events occur. With the default
        max_fills=1 this preserves the original one-shot behavior.
      multi_gaussian_fill:
        Same trigger rule, intended for repeated basin-memory fills. Configure
        max_fills, fill_cooldown_sec, and min_distance_between_fills to prevent
        rapid duplicate fills in the same basin.
    """

    def __init__(self):
        super().__init__("gaussian_fill")

        # Use Gazebo sim time
        self.set_parameters([
            rclpy.parameter.Parameter(
                'use_sim_time',
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])

        # ---- Parameters ----
        self.declare_parameter("escape_policy", "conditional_gaussian_fill")
        # Use float defaults so launch values like 5.0 (DOUBLE) are valid.
        self.declare_parameter("amplitude", 5.0)
        self.declare_parameter("min_sigma", 0.10)   # meters
        self.declare_parameter("max_sigma", 5.0)    # meters
        self.declare_parameter("min_points", 50)    # need enough history points
        self.declare_parameter("use_recent_fraction", 0.5)  # use freshest half
        self.declare_parameter("max_fills", 1)      # -1 means unlimited
        self.declare_parameter("fill_cooldown_sec", 0.0)
        self.declare_parameter("min_distance_between_fills", 0.0)

        self.escape_policy = self._normalize_policy(
            str(self.get_parameter("escape_policy").value)
        )
        self.A = float(self.get_parameter("amplitude").value)
        self.min_sigma = float(self.get_parameter("min_sigma").value)
        self.max_sigma = float(self.get_parameter("max_sigma").value)
        if self.max_sigma < self.min_sigma:
            self.get_logger().warn(
                "max_sigma was smaller than min_sigma; using min_sigma for both."
            )
            self.max_sigma = self.min_sigma
        self.min_points = max(1, int(self.get_parameter("min_points").value))
        self.use_recent_fraction = float(self.get_parameter("use_recent_fraction").value)
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

        self.fill_count = 0
        self.has_filled = False
        self.last_fill_time = None
        self.fill_centers = []
        self.buf_xy = None  # shape (N,2)

        self.sub_conv = self.create_subscription(
            StampedFloat64MultiArray,
            "/convergence_event",
            self.trigger_cb,
            10
        )

        self.sub_buffer = self.create_subscription(
            StampedFloat64MultiArray,
            "/pde_history",
            self.buffer_cb,
            10
        )

        self.pub = self.create_publisher(
            StampedFloat64MultiArray,
            "/cost_bias",
            10
        )

        self.get_logger().info(
            "GaussianFill ready (2D): "
            + f"policy={self.escape_policy}, A={self.A:.3f}, "
            + f"sigma=[{self.min_sigma:.3f}, {self.max_sigma:.3f}], "
            + f"max_fills={self.max_fills}, cooldown={self.fill_cooldown_sec:.3f}s, "
            + f"min_distance={self.min_distance_between_fills:.3f}m"
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
                f"Unknown escape_policy '{policy}'. Falling back to conditional_gaussian_fill."
            )
            return "conditional_gaussian_fill"
        return policy

    def buffer_cb(self, msg: StampedFloat64MultiArray):
        data = np.array(msg.data, dtype=np.float64)

        # Expect flattened [x0,y0,x1,y1,...]
        if data.size < 2 or (data.size % 2) != 0:
            return

        xy = data.reshape(-1, 2)

        if not np.all(np.isfinite(xy)):
            return

        self.buf_xy = xy

    def trigger_cb(self, msg: StampedFloat64MultiArray):
        if self.escape_policy == "none":
            return

        if self.max_fills == 0:
            return

        if self.max_fills > 0 and self.fill_count >= self.max_fills:
            return

        event_time = float(msg.timestamp)
        if (
            self.last_fill_time is not None
            and (event_time - self.last_fill_time) < self.fill_cooldown_sec
        ):
            remaining = self.fill_cooldown_sec - (event_time - self.last_fill_time)
            self.get_logger().info(
                f"Skipping fill: cooldown active for {remaining:.3f}s more."
            )
            return

        fill = self._fit_fill_to_history()
        if fill is None:
            return

        mu, sigma = fill

        if self._too_close_to_existing_fill(mu):
            self.get_logger().info(
                "Skipping fill: candidate center "
                + f"({mu[0]:.3f},{mu[1]:.3f}) is within "
                + f"{self.min_distance_between_fills:.3f}m of an existing fill."
            )
            return

        # Publish fill: [A, mu_x, mu_y, sigma]
        out = StampedFloat64MultiArray()
        out.header = "GaussianFill2D"
        out.timestamp = event_time
        out.data = [float(self.A), float(mu[0]), float(mu[1]), float(sigma)]
        self.pub.publish(out)

        self.fill_count += 1
        self.has_filled = self.fill_count > 0
        self.last_fill_time = event_time
        self.fill_centers.append(mu)
        self.get_logger().info(
            f"Published fill #{self.fill_count}: "
            + f"A={self.A:.3f}, mu=({mu[0]:.3f},{mu[1]:.3f}), sigma={sigma:.3f}"
        )

    def _fit_fill_to_history(self):
        if self.buf_xy is None or self.buf_xy.shape[0] < self.min_points:
            self.get_logger().warn(
                f"No sufficient 2D history for Gaussian fit "
                f"(have {0 if self.buf_xy is None else self.buf_xy.shape[0]} points)."
            )
            return None

        # Optionally use the most recent part (index 0 is freshest in PDE buffer)
        N = self.buf_xy.shape[0]
        n_use = max(self.min_points, int(self.use_recent_fraction * N))
        n_use = min(N, n_use)
        xy_use = self.buf_xy[:n_use, :]

        # Center estimate
        mu = np.mean(xy_use, axis=0)  # [mu_x, mu_y]

        # Radial sigma estimate: sqrt(E[||x-mu||^2])
        diffs = xy_use - mu[None, :]
        r2 = np.sum(diffs * diffs, axis=1)
        sigma = float(np.sqrt(np.mean(r2)))

        # Clamp sigma to safe bounds
        sigma = float(np.clip(sigma, self.min_sigma, self.max_sigma))

        return mu, sigma

    def _too_close_to_existing_fill(self, mu):
        if self.min_distance_between_fills <= 0.0 or not self.fill_centers:
            return False

        centers = np.array(self.fill_centers, dtype=np.float64)
        dists = np.linalg.norm(centers - mu[None, :], axis=1)
        return bool(np.min(dists) < self.min_distance_between_fills)


def main():
    rclpy.init()
    rclpy.spin(GaussianFill())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
