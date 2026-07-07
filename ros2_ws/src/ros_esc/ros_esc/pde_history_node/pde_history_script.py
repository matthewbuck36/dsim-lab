#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter
from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import StampedFloat64MultiArray


class PDEHistory(Node):
    """
    Transport-PDE style history buffer (upwind scheme) for 2D position.

    State: U[i, :] = [x, y] history at node i (i=0 is newest)
    PDE discretization:
        dU[0]/dt   =  lambda * (p - U[0])
        dU[i]/dt   =  lambda * (U[i-1] - U[i])   for i>=1

    Stability requires CFL: lambda * dt <= 1. We clamp dt to satisfy it.
    Publishes flattened buffer: [x0,y0,x1,y1,...]
    """

    def __init__(self):
        super().__init__("pde_history")

        # Use Gazebo simulation time
        self.set_parameters([
            rclpy.parameter.Parameter(
                'use_sim_time',
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])

        # ---- Parameters (match your paper settings) ----
        # N_buffer: number of nodes
        # k_periods: how many periods stored (used by convergence detector)
        # omega: dither frequency -> T = 2*pi/omega, kT = k*T, lambda = N/kT
        self.declare_parameter("n_buffer", 2000)
        self.declare_parameter("k_periods", 20)
        self.declare_parameter("omega", 5.0)
        self.declare_parameter("cfl", 0.9)  # < 1 for stability

        self.N = int(self.get_parameter("n_buffer").value)
        self.k = int(self.get_parameter("k_periods").value)
        self.omega = float(self.get_parameter("omega").value)
        self.cfl = float(self.get_parameter("cfl").value)

        # Derived
        self.T = 2.0 * np.pi / self.omega
        self.kT = self.k * self.T
        self.lambda_transport = self.N / self.kT  # matches your 1D script
        self.dt_node = self.kT / self.N          # dx in your script

        # Buffer U: shape (N, 2) for [x, y]
        self.U = np.zeros((self.N, 2), dtype=np.float64)

        self.last_stamp = None
        self.initialized = False

        # Sub odom
        self.sub = self.create_subscription(
            Odometry,
            "/odom",
            self.cb,
            10
        )

        # Pub history
        self.pub = self.create_publisher(
            StampedFloat64MultiArray,
            "/pde_history",
            10
        )

        self.get_logger().info(
            f"PDEHistory: N={self.N}, k={self.k}, omega={self.omega:.3f}, "
            f"lambda={self.lambda_transport:.3f}, dt_node={self.dt_node:.6f}"
        )

    def cb(self, msg: Odometry):
        # Current position boundary input p=[x,y]
        p = np.array(
            [msg.pose.pose.position.x, msg.pose.pose.position.y],
            dtype=np.float64
        )

        # Use sim time for dt (preferred)
        # If /clock not active, this still works once sim starts.
        now = self.get_clock().now().nanoseconds * 1e-9

        if self.last_stamp is None:
            self.U[:, :] = p
            self.last_stamp = now
            self.initialized = True
            return

        dt = now - self.last_stamp
        if dt <= 0.0:
            return

        # ---- CFL clamp (MAIN STABILITY FIX) ----
        dt_max = self.cfl / self.lambda_transport
        if dt > dt_max:
            dt = dt_max

        lam = self.lambda_transport

        # Upwind transport update
        dU = np.empty_like(self.U)
        dU[0, :] = lam * (p - self.U[0, :])
        dU[1:, :] = lam * (self.U[:-1, :] - self.U[1:, :])

        self.U = self.U + dt * dU
        self.last_stamp = now

        # Safety reset if NaN/Inf appears
        if not np.all(np.isfinite(self.U)):
            self.get_logger().warn("PDE buffer non-finite -> reset to current pose.")
            self.U[:, :] = p

        # Publish flattened buffer
        out = StampedFloat64MultiArray()
        out.header = "PDE History (x,y)"
        out.timestamp = float(now)  # keep consistent float seconds
        out.data = self.U.reshape(-1).tolist()
        self.pub.publish(out)


def main():
    rclpy.init()
    node = PDEHistory()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
