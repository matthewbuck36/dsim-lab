#!/usr/bin/env python3
"""Gazebo joint encoder; preserve the joint acquisition time in the legacy wire type."""

import argparse
import math

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from sensor_msgs.msg import JointState
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray
from ros_esc.clock_configuration import apply_legacy_sim_time_default


class EncoderNode(Node):
    def __init__(self):
        super().__init__("encoder_node")
        apply_legacy_sim_time_default(self)
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("input_joint_state_topic")
        parser.add_argument("input_timekeeping_topic")
        parser.add_argument("output_topic")
        parser.add_argument("--joint_names", nargs="+", required=True)
        args = parser.parse_args()
        self.start_time = None
        self.joint_names = args.joint_names
        self.encoder_publisher = self.create_publisher(StampedFloat64MultiArray, args.output_topic, 10)
        self.create_subscription(JointState, args.input_joint_state_topic, self.joint_state_callback, 10)
        self.create_subscription(Timekeeper, args.input_timekeeping_topic, self.timekeeping_callback, 10)

    def timekeeping_callback(self, msg):
        self.start_time = msg.start_time

    def joint_state_callback(self, msg):
        if self.start_time is None:
            return
        try:
            values = [float(msg.position[msg.name.index(name)]) for name in self.joint_names]
            source_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            if not all(math.isfinite(value) for value in values) or source_time < self.start_time:
                return
        except (ValueError, IndexError, TypeError):
            self.get_logger().warning("joint sample lacks finite configured encoder positions")
            return
        output = StampedFloat64MultiArray()
        output.header = "Encoder Values"
        output.timestamp = source_time - self.start_time
        output.data = values
        self.encoder_publisher.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = EncoderNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
