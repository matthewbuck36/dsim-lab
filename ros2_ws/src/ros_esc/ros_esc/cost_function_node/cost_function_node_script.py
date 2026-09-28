#!/usr/bin/env python3
"""Evaluate the existing modeled cost only on selected fresh sensor transforms."""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray, StampedTransformMultiArray
from ros_esc.clock_configuration import apply_legacy_sim_time_default
from ros_esc.config_parsing import parse_object_config


class CostFunction(Node):
    def __init__(self):
        super().__init__("cost_function_node")
        apply_legacy_sim_time_default(self)
        parser = argparse.ArgumentParser(description=__doc__)
        for name in ("input_transform_topic", "input_timekeeping_topic", "output_topic", "config"):
            parser.add_argument(name)
        parser.add_argument("--sample-rate-hz", type=float, default=0.0,
                            help="Maximum modeled acquisition rate; 0 keeps legacy unthrottled input")
        args = parser.parse_args()
        if not math.isfinite(args.sample_rate_hz) or args.sample_rate_hz < 0:
            parser.error("sample-rate-hz must be finite and nonnegative")
        config = json.loads(Path(args.config).expanduser().read_text())
        self.cost_function = parse_object_config(config["CostFunction"])
        self.noise_obj = parse_object_config(config["Noise"])
        self.sample_period = 1 / args.sample_rate_hz if args.sample_rate_hz else 0.0
        self.last_published_stamp = None
        self.start_time = None
        self.cost_publisher = self.create_publisher(StampedFloat64MultiArray, args.output_topic, 10)
        self.create_subscription(StampedTransformMultiArray, args.input_transform_topic, self.transform_callback, 10)
        self.create_subscription(Timekeeper, args.input_timekeeping_topic, self.timekeeping_callback, 10)

    def timekeeping_callback(self, msg):
        self.start_time = msg.start_time

    def transform_callback(self, msg):
        stamp = msg.timestamp
        if self.start_time is None or not math.isfinite(stamp) or not msg.transform_array:
            return
        if self.last_published_stamp is not None:
            elapsed = stamp - self.last_published_stamp
            if elapsed <= 0 or elapsed + 1e-9 < self.sample_period:
                return
        values = []
        for transform in msg.transform_array:
            matrix = create_transform_matrix(transform)
            if not np.isfinite(matrix).all():
                return
            values.append(float(self.cost_function.cost_output(stamp, matrix)))
        values = np.asarray(self.noise_obj.add_noise(stamp, np.array(values)))
        if not np.isfinite(values).all():
            return
        output = StampedFloat64MultiArray()
        output.header = "Cost Values"
        output.timestamp = stamp
        output.data = values.tolist()
        self.cost_publisher.publish(output)
        self.last_published_stamp = stamp


def create_transform_matrix(transform_object):
    """This converts a transform object into a transformation matrix."""

    # Get the translation portion in the transform object
    x_pos = transform_object.translation.x
    y_pos = transform_object.translation.y
    z_pos = transform_object.translation.z
    # Get the quaternions in the transform object
    quat_w = transform_object.rotation.w
    quat_x = transform_object.rotation.x
    quat_y = transform_object.rotation.y
    quat_z = transform_object.rotation.z

    # Package this position and orientation data into a homogeneous transformation matrix
    # Note this transformation matrix represents the position & orientation of the vehicle
    # in the stationary odometry frame. The rotation matrix was constructed using eqn (7b):
    # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    transform_matrix = np.array([
        [
            1-2*quat_y**2-2*quat_z**2,
            2*quat_x*quat_y-2*quat_w*quat_z,
            2*quat_x*quat_z+2*quat_w*quat_y,
            x_pos
        ],
        [
            2*quat_x*quat_y+2*quat_w*quat_z,
            1-2*quat_x**2-2*quat_z**2,
            2*quat_y*quat_z-2*quat_w*quat_x,
            y_pos
        ],

        [
            2*quat_x*quat_z-2*quat_w*quat_y,
            2*quat_y*quat_z+2*quat_w*quat_x,
            1-2*quat_x**2-2*quat_y**2,
            z_pos
        ],
        [0,0,0,1]
    ])

    return transform_matrix


def main(args=None):
    rclpy.init(args=args)
    node = CostFunction()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
