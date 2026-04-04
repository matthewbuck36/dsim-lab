#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter
from ros_esc_interfaces.msg import StampedFloat64MultiArray


class ConvergenceDetector(Node):
    """
    Integral convergence metric using PDE transport buffer.

    For 2D:
      U is (N,2) trajectory history.
      r = ∫ ||U_recent(s) - U_old(s)||^2 ds  ~ sum(||diff||^2)*dt_node

    metric = r + exp(-b*(t-t0)) - threshold
    Trigger when metric crosses below 0 (we approximate by checking metric < 0).
    """

    def __init__(self):
        super().__init__("convergence_detector")

        # Use Gazebo simulation time
        self.set_parameters([
            rclpy.parameter.Parameter(
                'use_sim_time',
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])
    

        # Params
        self.declare_parameter("k_periods", 20)
        # Threshold must be positive; with threshold=0 the metric
        # r + exp(-b(t-t0)) - threshold is nonnegative and never crosses below zero.
        self.declare_parameter("threshold", 0.2)
        self.declare_parameter("decay_rate", 0.15)

        # Must match PDEHistory omega, n_buffer to get correct dt_node, fill time
        self.declare_parameter("n_buffer", 2000)
        self.declare_parameter("omega", 5.0)

        # Startup gating
        self.declare_parameter("min_fill_periods", 1.0)  # require >= 1*kT before trigger

        self.k = int(self.get_parameter("k_periods").value)
        self.th = float(self.get_parameter("threshold").value)
        self.b = float(self.get_parameter("decay_rate").value)

        self.N = int(self.get_parameter("n_buffer").value)
        self.omega = float(self.get_parameter("omega").value)
        self.T = 2.0 * np.pi / self.omega
        self.kT = self.k * self.T
        self.dt_node = self.kT / self.N

        self.min_fill_periods = float(self.get_parameter("min_fill_periods").value)
        self.min_time_before_trigger = self.min_fill_periods * self.kT

        self.t0 = None
        self.first_time = None
        self.last_metric = None

        self.sub = self.create_subscription(
            StampedFloat64MultiArray,
            "/pde_history",
            self.buffer_cb,
            10
        )

        self.pub = self.create_publisher(
            StampedFloat64MultiArray,
            "/convergence_event",
            10
        )

        # in __init__ (add this)
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

        self.get_logger().info(
            f"ConvergenceDetector: k={self.k}, th={self.th}, b={self.b}, "
            f"N={self.N}, omega={self.omega:.3f}, dt_node={self.dt_node:.6f}, "
            f"min_trigger_time={self.min_time_before_trigger:.2f}s"
        )

    def buffer_cb(self, msg: StampedFloat64MultiArray):
        t = float(msg.timestamp)

        if self.first_time is None:
            self.first_time = t

        # Parse flat [x0,y0,x1,y1,...] -> (N,2)
        data = np.array(msg.data, dtype=np.float64)
        if data.size < 2:
            return
        if data.size % 2 != 0:
            # malformed
            return

        U = data.reshape(-1, 2)  # shape (N,2) if consistent

        if not np.all(np.isfinite(U)):
            return

        N = U.shape[0]
        if N < self.k * 3:
            # Not enough nodes to form 0:M and 2M:3M
            return

        M = N // self.k
        if 3 * M > N or M <= 0:
            return

        # Startup gating: avoid false positives before buffer meaningfully represents history
        if (t - self.first_time) < self.min_time_before_trigger:
            return

        if self.t0 is None:
            self.t0 = t
            return

        seg_recent = U[0:M, :]
        seg_old = U[2*M:3*M, :]

        diff = seg_recent - seg_old
        # ||diff||^2 per node
        diff_sq = np.sum(diff * diff, axis=1)  # (M,)
        r_val = float(np.sum(diff_sq) * self.dt_node)


        decay_term = float(np.exp(-self.b * (t - self.t0)))
        metric = r_val + decay_term - self.th

        # in buffer_cb (right after computing metric)
        metric_msg = StampedFloat64MultiArray()
        metric_msg.header = "CONV_METRIC"
        metric_msg.timestamp = t
        metric_msg.data = [float(metric)]
        self.pub_metric.publish(metric_msg)

        m = StampedFloat64MultiArray()
        m.header = "R_VAL"
        m.timestamp = t
        m.data = [float(r_val)]
        self.pub_r.publish(m) 

        # Optional: require sign change (prevents repeated triggers due to noise)
        if self.last_metric is None:
            self.last_metric = metric
            return

        crossed = (self.last_metric > 0.0) and (metric < 0.0)
        self.last_metric = metric

        if crossed:
            out = StampedFloat64MultiArray()
            out.header = "CONVERGED"
            out.timestamp = t
            out.data = [metric, r_val, decay_term]
            self.pub.publish(out)
            self.get_logger().info(
                "Convergence event: "
                + f"metric={metric:.6f}, r={r_val:.6f}, decay={decay_term:.6f}, t={t:.3f}"
            )

            # Reset decay reference like your script
            self.t0 = t


def main():
    rclpy.init()
    rclpy.spin(ConvergenceDetector())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
