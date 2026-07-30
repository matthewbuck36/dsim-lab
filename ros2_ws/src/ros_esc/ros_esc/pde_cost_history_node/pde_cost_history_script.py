#!/usr/bin/env python3

import rclpy
import numpy as np
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
import rclpy.parameter

from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown
from ros_esc.search_epoch import SearchEpochGate
from ros_esc.supervisor_node.state_machine import (
    ROBUST_PROFILE,
    VALID_PROFILES,
)
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray
from std_msgs.msg import Float64MultiArray


class PDECostHistory(Node):
    """
    PDE-style history buffer for scalar cost function data.

    Subscribes:
        /turtlebot3/cost_value_chatter
        type: ros_esc_interfaces/msg/StampedFloat64MultiArray

    Publishes:
        /pde_cost_history
        type: std_msgs/msg/Float64MultiArray

    Output:
        data = [J0, J1, J2, ..., JN-1]

    where:
        J0 is the newest cost value.
    """

    def __init__(self, parameter_overrides=None):
        super().__init__(
            "pde_cost_history",
            parameter_overrides=parameter_overrides,
        )

        # Use Gazebo simulation time
        self.set_parameters([
            rclpy.parameter.Parameter(
                "use_sim_time",
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])

        # Parameters
        self.declare_parameter("n_buffer", 2000)
        self.declare_parameter("k_periods", 20)
        self.declare_parameter("omega", 5.0)
        self.declare_parameter("cfl", 0.9)
        self.declare_parameter("cost_topic", "/turtlebot3/cost_value_chatter")
        self.declare_parameter("algorithm_profile", "legacy")
        self.declare_parameter(
            "robust_search_epoch_reset_enabled", False
        )
        self.declare_parameter(
            "algorithm_state_topic",
            "/gesc_gaussian/algorithm_state",
        )

        self.N = int(self.get_parameter("n_buffer").value)
        self.k = int(self.get_parameter("k_periods").value)
        self.omega = float(self.get_parameter("omega").value)
        self.cfl = float(self.get_parameter("cfl").value)
        self.cost_topic = str(self.get_parameter("cost_topic").value)
        self.algorithm_profile = str(
            self.get_parameter("algorithm_profile").value
        ).strip()
        if self.algorithm_profile not in VALID_PROFILES:
            raise ValueError(
                f"algorithm_profile must be one of {VALID_PROFILES}"
            )
        self.search_epoch_reset_enabled = bool(
            self.get_parameter(
                "robust_search_epoch_reset_enabled"
            ).value
        )
        if (
            self.search_epoch_reset_enabled
            and self.algorithm_profile != ROBUST_PROFILE
        ):
            raise ValueError(
                "robust search-epoch reset requires robust_gaussian_v1"
            )

        # Derived PDE parameters
        self.T = 2.0 * np.pi / self.omega
        self.kT = self.k * self.T
        self.lambda_transport = self.N / self.kT
        self.dt_node = self.kT / self.N

        # Scalar PDE history buffer
        self.U = np.zeros(self.N, dtype=np.float64)

        self.last_stamp = None
        self.search_epoch_gate = SearchEpochGate(
            self.search_epoch_reset_enabled
        )
        self.search_epoch_reset_pending = False

        # Subscribe to cost function array
        self.sub = self.create_subscription(
            StampedFloat64MultiArray,
            self.cost_topic,
            self.cb,
            10
        )
        self.algorithm_state_subscriber = None
        if self.search_epoch_reset_enabled:
            self.algorithm_state_subscriber = self.create_subscription(
                AlgorithmState,
                str(self.get_parameter("algorithm_state_topic").value),
                self.algorithm_state_cb,
                10,
            )

        # Publish standard Float64MultiArray so ros2 topic echo works easily
        self.pub = self.create_publisher(
            Float64MultiArray,
            "/pde_cost_history",
            10
        )

        self.get_logger().info(
            f"PDECostHistory started. "
            f"Subscribing to {self.cost_topic} as StampedFloat64MultiArray. "
            f"Publishing /pde_cost_history as std_msgs/msg/Float64MultiArray. "
            f"N={self.N}, k={self.k}, omega={self.omega:.3f}, "
            f"lambda={self.lambda_transport:.3f}, dt_node={self.dt_node:.6f}, "
            f"search_epoch_reset={self.search_epoch_reset_enabled}"
        )

    def algorithm_state_cb(self, msg):
        """Arm one reset for the next finite cost on each SEARCH entry."""
        boundary = self.search_epoch_gate.update(msg)
        if boundary == SearchEpochGate.ENTERED:
            self.search_epoch_reset_pending = True

    def cb(self, msg: StampedFloat64MultiArray):
        # The cost value is assumed to be the first element of msg.data
        if len(msg.data) == 0:
            self.get_logger().warn("Received empty cost array.")
            return

        J = float(msg.data[0])

        # Use simulation clock
        now = self.get_clock().now().nanoseconds * 1e-9

        if self.search_epoch_reset_pending and not np.isfinite(J):
            return

        if self.search_epoch_reset_pending:
            self.U[:] = J
            self.last_stamp = now
            self.search_epoch_reset_pending = False
            self.publish_history()
            return

        # First message initializes the whole history buffer
        if self.last_stamp is None:
            self.U[:] = J
            self.last_stamp = now
            self.publish_history()
            return

        dt = now - self.last_stamp
        if dt <= 0.0:
            return

        # CFL stability clamp
        dt_max = self.cfl / self.lambda_transport
        if dt > dt_max:
            dt = dt_max

        lam = self.lambda_transport

        # Upwind transport update
        dU = np.empty_like(self.U)
        dU[0] = lam * (J - self.U[0])
        dU[1:] = lam * (self.U[:-1] - self.U[1:])

        self.U = self.U + dt * dU
        self.last_stamp = now

        # Safety reset
        if not np.all(np.isfinite(self.U)):
            self.get_logger().warn("PDE cost buffer non-finite -> reset to current cost.")
            self.U[:] = J

        self.publish_history()

    def publish_history(self):
        out = Float64MultiArray()
        out.data = self.U.tolist()
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = PDECostHistory()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    with DeferredSignalShutdown() as shutdown:
        try:
            while rclpy.ok() and not shutdown.requested:
                executor.spin_once(timeout_sec=0.05)
        except KeyboardInterrupt:
            shutdown.request()
        finally:
            executor.remove_node(node)
            try:
                executor.shutdown()
            finally:
                try:
                    node.destroy_node()
                finally:
                    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
