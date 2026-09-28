#!/usr/bin/env python3
"""Observed odometry plus encoder angle -> sensor transform at the encoder stamp."""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Transform
from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray, StampedTransformMultiArray
from ros_esc.clock_configuration import apply_legacy_sim_time_default
from ros_esc.config_parsing import parse_object_config


class SensorPosition(Node):
    def __init__(self):
        super().__init__("sensor_position_node")
        apply_legacy_sim_time_default(self)
        parser = argparse.ArgumentParser(description=__doc__)
        for name in ("input_odom_topic", "input_enc_topic", "input_timekeeping_topic", "output_topic", "config"):
            parser.add_argument(name)
        args = parser.parse_args()
        config = json.loads(Path(args.config).expanduser().read_text())
        self.objects_list = [parse_object_config(value) for value in config.values()]
        self.start_time = None
        self.odom_data = None
        self.sensor_pose_publisher = self.create_publisher(StampedTransformMultiArray, args.output_topic, 10)
        self.create_subscription(Odometry, args.input_odom_topic, self.pose_callback, 10)
        self.create_subscription(StampedFloat64MultiArray, args.input_enc_topic, self.encoder_callback, 10)
        self.create_subscription(Timekeeper, args.input_timekeeping_topic, self.timekeeping_callback, 10)

    def timekeeping_callback(self, msg):
        self.start_time = msg.start_time

    def pose_callback(self, msg):
        p, q = msg.pose.pose.position, msg.pose.pose.orientation
        values = [p.x, p.y, p.z, q.w, q.x, q.y, q.z]
        if all(math.isfinite(value) for value in values):
            self.odom_data = values

    def encoder_callback(self, msg):
        if self.start_time is None or self.odom_data is None:
            return
        if (len(msg.data) != len(self.objects_list) or not math.isfinite(msg.timestamp)
                or not all(math.isfinite(value) for value in msg.data)):
            return
        output = StampedTransformMultiArray()
        output.header = "Sensor Transformation Matrices"
        output.timestamp = msg.timestamp
        for transform_object, angle in zip(self.objects_list, msg.data):
            matrix = transform_object.transform_output(self.odom_data, angle)
            if not np.isfinite(matrix).all():
                return
            transform = Transform()
            transform.translation.x, transform.translation.y, transform.translation.z = map(float, matrix[:3, 3])
            qw, qx, qy, qz = calculate_quaternions(matrix)
            transform.rotation.w, transform.rotation.x = float(qw), float(qx)
            transform.rotation.y, transform.rotation.z = float(qy), float(qz)
            output.transform_array.append(transform)
        self.sensor_pose_publisher.publish(output)


def calculate_quaternions(transform_matrix):
    """This calculates quaternion angles from a transformation matrix.

    See https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    eqns (8 thru 9) for more information on this procedure.
    """

    # Pull data from the transform matrix
    r11 = transform_matrix[0][0]
    r12 = transform_matrix[0][1]
    r13 = transform_matrix[0][2]
    r21 = transform_matrix[1][0]
    r22 = transform_matrix[1][1]
    r23 = transform_matrix[1][2]
    r31 = transform_matrix[2][0]
    r32 = transform_matrix[2][1]
    r33 = transform_matrix[2][2]

    # Find the magnitude of each quaternion component
    mag_q0 = np.sqrt((1+r11+r22+r33)/4)
    mag_q1 = np.sqrt((1+r11-r22-r33)/4)
    mag_q2 = np.sqrt((1-r11+r22-r33)/4)
    mag_q3 = np.sqrt((1-r11-r22+r33)/4)

    # Find the largest magnitude of the above, assume its sign is positive
    largest = max(mag_q0, mag_q1, mag_q2, mag_q3)

    # pylint: disable=invalid-name
    # If mag_q0 is largest
    if largest == mag_q0:
        qw = mag_q0
        qx = (r32-r23)/(4*mag_q0)
        qy = (r13-r31)/(4*mag_q0)
        qz = (r21-r12)/(4*mag_q0)

    # If mag_q1 is largest
    elif largest == mag_q1:
        qw = (r32-r23)/(4*mag_q1)
        qx = mag_q1
        qy = (r12+r21)/(4*mag_q1)
        qz = (r13+r31)/(4*mag_q1)

    # If mag_q2 is largest
    elif largest == mag_q2:
        qw = (r13-r31)/(4*mag_q2)
        qx = (r12+r21)/(4*mag_q2)
        qy = mag_q2
        qz = (r23+r32)/(4*mag_q2)

    # If mag_q3 is largest
    else:
        qw = (r21-r12)/(4*mag_q3)
        qx = (r13+r31)/(4*mag_q3)
        qy = (r23+r32)/(4*mag_q3)
        qz = mag_q3

    return qw, qx, qy, qz # pylint: enable=invalid-name


def main(args=None):
    rclpy.init(args=args)
    node = SensorPosition()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
