#!/usr/bin/env python3
import argparse
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
    Adds dynamic 2D Gaussian fills to the cost output WITHOUT changing the original cost function node.

    Inputs:
      - /turtlebot3/cost_value_chatter : StampedFloat64MultiArray (N cost values, e.g. rotating sensors)
      - /odom                          : nav_msgs/Odometry (robot pose)
      - /cost_bias                     : StampedFloat64MultiArray [A, mu_x, mu_y, sigma] (one-shot)

    Output:
      - /cost_modified                 : StampedFloat64MultiArray (same length as input cost array)
    """

    def __init__(self):
        super().__init__("modified_cost_2d")

        # Parse input/output topics from CLI so launch files can wire this node.
        parser = argparse.ArgumentParser(
            description="Add Gaussian fill bias to cost values."
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
        # Keep unknown CLI tokens for rclpy/ROS argument handling.
        args, _ = parser.parse_known_args()

        # Use Gazebo sim time
        self.set_parameters([
            rclpy.parameter.Parameter(
                "use_sim_time",
                rclpy.parameter.Parameter.Type.BOOL,
                True
            )
        ])

        # ---- Parameters ----
        # If true: add same bias to every sensor cost entry to keep dimensions identical.
        # If false: only modify the first entry and pass through others.
        self.declare_parameter("bias_all_channels", True)
        self.bias_all = bool(self.get_parameter("bias_all_channels").value)

        # Store fill terms: list[(A, mu_x, mu_y, sigma)]
        self.terms = []

        # Latest robot center position (fallback if sensor transform is unavailable)
        self.xy = None  # np.array([x, y])
        # Latest sensor positions from rotating frame output (preferred for modulation)
        self.sensor_xy = None  # np.ndarray shape (M, 2)

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
            "ModifiedCost2D started. Waiting for sensor/cost/fill streams."
        )

    def odom_cb(self, msg: Odometry):
        p = msg.pose.pose.position
        self.xy = np.array([p.x, p.y], dtype=np.float64)

    def sensor_cb(self, msg: StampedTransformMultiArray):
        # Track all sensor coordinates so fill bias can be evaluated at each channel.
        if len(msg.transform_array) == 0:
            return
        xy = []
        for tf in msg.transform_array:
            xy.append([tf.translation.x, tf.translation.y])
        self.sensor_xy = np.array(xy, dtype=np.float64)

    def fill_cb(self, msg: StampedFloat64MultiArray):
        data = list(msg.data)

        # Expect [A, mu_x, mu_y, sigma]
        if len(data) != 4:
            self.get_logger().warn(
                f"Received /cost_bias with len={len(data)}; expected 4: [A, mu_x, mu_y, sigma]. Ignoring."
            )
            return

        A, mu_x, mu_y, sigma = map(float, data)

        if not np.isfinite([A, mu_x, mu_y, sigma]).all():
            self.get_logger().warn("Received NaN/Inf in /cost_bias. Ignoring.")
            return

        sigma = max(sigma, 1e-6)
        self.terms.append((A, mu_x, mu_y, sigma))

        self.get_logger().info(
            f"Added fill term: A={A:.3f}, mu=({mu_x:.3f},{mu_y:.3f}), sigma={sigma:.3f} "
            f"(total terms={len(self.terms)})"
        )

    def _bias_at_xy(self, x: float, y: float) -> float:
        """Compute total Gaussian bias at current (x,y)."""
        if not self.terms:
            return 0.0

        bias = 0.0
        for A, mu_x, mu_y, sigma in self.terms:
            dx = x - mu_x
            dy = y - mu_y
            r2 = dx * dx + dy * dy
            bias += A * np.exp(-r2 / (2.0 * sigma * sigma))
        return float(bias)

    def cost_cb(self, msg: StampedFloat64MultiArray):
        if self.xy is None and self.sensor_xy is None:
            # No pose information yet.
            return

        cost_vals = np.array(msg.data, dtype=np.float64)
        if cost_vals.size == 0:
            return

        # Preferred path: evaluate bias per sensor channel from rotating sensor pose.
        if self.sensor_xy is not None and self.sensor_xy.shape[0] == cost_vals.size:
            biases = np.array(
                [self._bias_at_xy(float(x), float(y)) for x, y in self.sensor_xy],
                dtype=np.float64
            )
            if self.bias_all:
                cost_out = (cost_vals + biases).tolist()
            else:
                cost_out = cost_vals.copy()
                cost_out[0] = cost_out[0] + biases[0]
                cost_out = cost_out.tolist()
        else:
            # Fallback path: evaluate bias at robot center.
            x, y = float(self.xy[0]), float(self.xy[1])
            bias = self._bias_at_xy(x, y)
            if self.bias_all:
                cost_out = (cost_vals + bias).tolist()
            else:
                cost_out = cost_vals.copy()
                cost_out[0] = cost_out[0] + bias
                cost_out = cost_out.tolist()

        out = StampedFloat64MultiArray()
        out.header = "Modified Cost 2D"
        out.timestamp = msg.timestamp
        out.data = [float(v) for v in cost_out]
        self.pub.publish(out)


def main():
    rclpy.init()
    rclpy.spin(ModifiedCost2D())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
