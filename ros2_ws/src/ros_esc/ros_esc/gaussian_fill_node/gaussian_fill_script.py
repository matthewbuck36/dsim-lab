#!/usr/bin/env python3

import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter
from scipy.optimize import least_squares

from ros_esc_interfaces.msg import StampedFloat64MultiArray
from std_msgs.msg import Float64MultiArray


class GaussianFill(Node):
    """
    Adds Gaussian fills at detected trap locations.

    - Reads 2D position history from /pde_history as [x0,y0,x1,y1,...].
    - Reads PDE cost history from /pde_cost_history.
    - On /convergence_event, fits an inverted Gaussian basin to history:
      A * exp(-||xy - mu||^2 / v) + c ~= -J(xy).
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
        self.declare_parameter("fit_min_amplitude", 0.15)
        self.declare_parameter("fit_max_amplitude", 10.0)
        self.declare_parameter("fit_offset_bound", 10.0)

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

        self.fill_count = 0
        self.has_filled = False
        self.last_fill_time = None
        self.fill_centers = []

        self.buf_xy = None
        self.buf_cost = None

        # ---- Subscribers ----
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

        self.sub_cost_history = self.create_subscription(
            Float64MultiArray,
            "/pde_cost_history",
            self.cost_history_cb,
            10
        )

        # ---- Publisher ----
        self.pub = self.create_publisher(
            StampedFloat64MultiArray,
            "/cost_bias",
            10
        )

        self.get_logger().info(
            "GaussianFill ready (2D): "
            + f"policy={self.escape_policy}, "
            + f"fallback_A={self.A:.3f}, "
            + f"fit_A=[{self.fit_min_amplitude:.3f}, {self.fit_max_amplitude:.3f}], "
            + f"sigma=[{self.min_sigma:.3f}, {self.max_sigma:.3f}], "
            + f"max_fills={self.max_fills}, "
            + f"cooldown={self.fill_cooldown_sec:.3f}s, "
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
                f"Unknown escape_policy '{policy}'. "
                "Falling back to conditional_gaussian_fill."
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
        if self.escape_policy == "none":
            return

        if self.max_fills == 0:
            return

        if self.A <= 0.0:
            self.get_logger().info(
                "Skipping fill: gaussian fill amplitude is <= 0.0."
            )
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

        A, mu, sigma, fitted_A = fill

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
        out.data = [
            float(A),
            float(mu[0]),
            float(mu[1]),
            float(sigma),
        ]

        self.pub.publish(out)

        self.fill_count += 1
        self.has_filled = self.fill_count > 0
        self.last_fill_time = event_time
        self.fill_centers.append(mu)

        self.get_logger().info(
            f"Published fill #{self.fill_count}: "
            + f"A={A:.3f}, "
            + f"fitted_A={fitted_A:.3f}, "
            + f"cost_mean={self.pde_cost_mean:.3f}, "
            + f"mu=({mu[0]:.3f},{mu[1]:.3f}), "
            + f"sigma={sigma:.3f}"
        )

    def _gaussian_model(self, params, xy):
        """A * exp(-||xy-mu||^2 / v) + c, using v = 2*sigma^2."""
        A, mu_x, mu_y, v, c = params
        v = max(float(v), 1e-9)
        dx = xy[:, 0] - mu_x
        dy = xy[:, 1] - mu_y
        r2 = dx * dx + dy * dy
        return A * np.exp(-r2 / v) + c

    def _fit_fill_to_history(self):
        if self.buf_xy is None or self.buf_xy.shape[0] < self.min_points:
            self.get_logger().warn(
                f"No sufficient 2D history for Gaussian fit "
                f"(have {0 if self.buf_xy is None else self.buf_xy.shape[0]} points)."
            )
            return None

        if self.buf_cost is None or self.buf_cost.size < self.min_points:
            self.get_logger().warn(
                f"No sufficient cost history for Gaussian fit "
                f"(have {0 if self.buf_cost is None else self.buf_cost.size} points)."
            )
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
            self.get_logger().warn("Non-finite history found during Gaussian fit.")
            return None

        # Prevent ill-conditioned fits when the recent trajectory has collapsed
        # to a single point. This mirrors the pasted script's static-data guard.
        if np.max(np.std(xy_use, axis=0)) < 1e-4:
            self.get_logger().warn("Position history variance too low for Gaussian fit.")
            return None

        target_y = -cost_use

        c_guess = float(np.min(target_y))
        c_guess = float(np.clip(c_guess, -self.fit_offset_bound, self.fit_offset_bound))
        A_guess = float(np.max(target_y) - c_guess)
        A_guess = float(np.clip(A_guess, 0.0, self.fit_max_amplitude))
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
        lb = [
            0.0,
            -np.inf,
            -np.inf,
            v_min,
            -self.fit_offset_bound,
        ]
        ub = [
            self.fit_max_amplitude,
            np.inf,
            np.inf,
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
            self.get_logger().warn(f"Gaussian fit failed: {exc}")
            return None

        if not res.success:
            self.get_logger().warn(f"Gaussian fit did not converge: {res.message}")
            return None

        A, mu_x, mu_y, v, _ = res.x

        if A < self.fit_min_amplitude:
            self.get_logger().info(
                f"Skipping fill: fitted basin amplitude {A:.3f} "
                f"is below threshold {self.fit_min_amplitude:.3f}."
            )
            return None

        sigma = float(np.sqrt(max(v, 0.0) / 2.0))
        sigma = float(np.clip(sigma, self.min_sigma, self.max_sigma))
        mu = np.array([mu_x, mu_y], dtype=np.float64)

        return self.A, mu, sigma, float(A)

    def _too_close_to_existing_fill(self, mu):
        if self.min_distance_between_fills <= 0.0 or not self.fill_centers:
            return False

        centers = np.array(self.fill_centers, dtype=np.float64)
        dists = np.linalg.norm(centers - mu[None, :], axis=1)

        return bool(np.min(dists) < self.min_distance_between_fills)


def main():
    rclpy.init()
    node = GaussianFill()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
