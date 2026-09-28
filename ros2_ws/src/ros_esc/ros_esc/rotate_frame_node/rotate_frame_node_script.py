#!/usr/bin/env python3
"""Gazebo arm command owner and the original 30 Hz experiment Timekeeper."""

import argparse
import json
import math
from pathlib import Path
import signal

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import Float64MultiArray
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray
from ros_esc.clock_configuration import apply_legacy_sim_time_default
from ros_esc.config_parsing import parse_object_config


class RotateFrame(Node):
    def __init__(self):
        super().__init__("rotate_arm")
        apply_legacy_sim_time_default(self)
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("input_enc_topic")
        parser.add_argument("output_timekeeper_topic")
        parser.add_argument("config")
        args = parser.parse_args()
        config = json.loads(Path(args.config).expanduser().read_text())
        self.objects_list = [parse_object_config(value) for value in config.values()]
        self.publishers_list = [self.create_publisher(Float64MultiArray, f"/{name}/commands", 10)
                                for name in config]
        self.spin_directions = [None] * len(self.objects_list)
        self.stopped = False
        self.start_time = self.get_clock().now().nanoseconds * 1e-9
        self.create_subscription(StampedFloat64MultiArray, args.input_enc_topic, self.encoder_callback, 10)
        self.timekeeper_publisher = self.create_publisher(Timekeeper, args.output_timekeeper_topic, 150)
        self.create_timer(1 / 30, self.publish_timekeeper_reading)

    def encoder_callback(self, msg):
        if self.stopped or len(msg.data) != len(self.objects_list):
            return
        now = self.get_clock().now().nanoseconds * 1e-9 - self.start_time
        for i, (profile, publisher, angle) in enumerate(zip(self.objects_list, self.publishers_list, msg.data)):
            if not math.isfinite(angle):
                self.stop()
                return
            speed = float(profile.velocity_output(now, angle, self.spin_directions[i]))
            if not math.isfinite(speed):
                self.stop()
                return
            if speed:
                self.spin_directions[i] = speed > 0
            output = Float64MultiArray()
            output.data = [speed]
            publisher.publish(output)

    def publish_timekeeper_reading(self):
        output = Timekeeper()
        output.start_time = self.start_time
        output.mode = "sim time" if self.get_parameter("use_sim_time").value else "real time"
        self.timekeeper_publisher.publish(output)

    def stop(self):
        """Latch neutral before shutting down; no later callback may restart the arm."""
        self.stopped = True
        for publisher in self.publishers_list:
            output = Float64MultiArray()
            output.data = [0.0]
            publisher.publish(output)


def main(args=None):
    # Keep the context alive long enough to publish neutral on Ctrl+C/SIGTERM.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    def interrupt(_signal, _frame):
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupt)
    node = RotateFrame()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        rclpy.spin_once(node, timeout_sec=0.05)
        node.destroy_node()
        rclpy.try_shutdown()
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    main()
