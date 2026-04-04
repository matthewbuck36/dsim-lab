#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter
from ros_esc_interfaces.msg import StampedFloat64MultiArray


class GaussianFill(Node):
    """
    Adds a Gaussian fill ONCE at the first detected trap location.
    - Reads 2D position history from /pde_history as [x0,y0,x1,y1,...].
    - On /convergence_event (metric crossed), computes (mu_x, mu_y) and sigma.
    - Publishes /cost_bias once: [A, mu_x, mu_y, sigma].
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
        # Use float defaults so launch values like 5.0 (DOUBLE) are valid.
        self.declare_parameter("amplitude", 5.0)
        self.declare_parameter("min_sigma", 0.10)   # meters
        self.declare_parameter("max_sigma", 5.0)    # meters
        self.declare_parameter("min_points", 50)    # need enough history points
        self.declare_parameter("use_recent_fraction", 0.5)  # use freshest half

        self.A = float(self.get_parameter("amplitude").value)
        self.min_sigma = float(self.get_parameter("min_sigma").value)
        self.max_sigma = float(self.get_parameter("max_sigma").value)
        self.min_points = int(self.get_parameter("min_points").value)
        self.use_recent_fraction = float(self.get_parameter("use_recent_fraction").value)

        self.has_filled = False
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

        self.get_logger().info("GaussianFill ready (2D, one-shot).")

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
        if self.has_filled:
            return

        if self.buf_xy is None or self.buf_xy.shape[0] < self.min_points:
            self.get_logger().warn(
                f"No sufficient 2D history for Gaussian fit "
                f"(have {0 if self.buf_xy is None else self.buf_xy.shape[0]} points)."
            )
            return

        # Optionally use the most recent part (index 0 is freshest in PDE buffer)
        N = self.buf_xy.shape[0]
        n_use = max(self.min_points, int(self.use_recent_fraction * N))
        xy_use = self.buf_xy[:n_use, :]

        # Center estimate
        mu = np.mean(xy_use, axis=0)  # [mu_x, mu_y]

        # Radial sigma estimate: sqrt(E[||x-mu||^2])
        diffs = xy_use - mu[None, :]
        r2 = np.sum(diffs * diffs, axis=1)
        sigma = float(np.sqrt(np.mean(r2)))

        # Clamp sigma to safe bounds
        sigma = float(np.clip(sigma, self.min_sigma, self.max_sigma))

        # Publish fill once: [A, mu_x, mu_y, sigma]
        out = StampedFloat64MultiArray()
        out.header = "GaussianFill2D"
        out.timestamp = msg.timestamp
        out.data = [float(self.A), float(mu[0]), float(mu[1]), float(sigma)]
        self.pub.publish(out)

        self.has_filled = True
        self.get_logger().info(
            f"Published ONE fill: A={self.A:.3f}, mu=({mu[0]:.3f},{mu[1]:.3f}), sigma={sigma:.3f}"
        )


def main():
    rclpy.init()
    rclpy.spin(GaussianFill())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
