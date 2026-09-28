#!/usr/bin/env python3
"""Original configurable ESC filter, with bounded integration and source-age checks."""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.parameter import Parameter
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray
from ros_esc.config_parsing import parse_filter_config

INPUT_EXPIRY_SEC = 0.5
MAX_REFINEMENT_EVALUATIONS = 64


def _argument_bool(value):
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value!r}")


def parse_filter_arguments(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("inp_value_topic", "inp_encoder_topic", "inp_timekeeping_topic", "out_topic"):
        parser.add_argument(name)
    parser.add_argument("--filter_file", dest="json_config", required=True)
    parser.add_argument("--append_encoder_data", "--combine_enc_data", dest="combine_enc_data",
                        type=_argument_bool, default=False)
    parser.add_argument("--use-sim-time", type=_argument_bool, default=True)
    return parser.parse_args(arguments)


def advance_filter_state(custom_filter, previous_time, current_time, inputs, state, derivative):
    """Retain original Euler/refinement order within a finite derivative budget.

    The ordinary valid one-step path is unchanged. Failed candidates are
    retried from the original state with m=2,3,... subdivisions, using the
    original evaluation times. Exhaustion never publishes a partial result.
    """
    dt = current_time - previous_time
    if not math.isfinite(dt) or dt < 0:
        raise ValueError("filter time is invalid")
    state = np.asarray(state, dtype=float)
    candidate = state + dt * np.asarray(derivative, dtype=float)
    if np.isfinite(candidate).all() and custom_filter.valid_state(candidate):
        return candidate
    evaluations = 1  # caller supplied the first derivative
    for subdivisions in range(2, MAX_REFINEMENT_EVALUATIONS + 1):
        if evaluations + subdivisions > MAX_REFINEMENT_EVALUATIONS:
            break
        candidate = state.copy()
        increment = dt / subdivisions
        for part in range(subdivisions):
            change = np.asarray(custom_filter.differential_equation(
                current_time + part * increment, candidate, inputs), dtype=float)
            evaluations += 1
            candidate = candidate + increment * change
        if np.isfinite(candidate).all() and custom_filter.valid_state(candidate):
            return candidate
    raise ValueError("filter refinement exhausted its 64-evaluation budget")


class CustomFilter(Node):
    def __init__(self):
        args = parse_filter_arguments()
        super().__init__("custom_filter")
        self.set_parameters([Parameter("use_sim_time", Parameter.Type.BOOL, args.use_sim_time)])
        config = json.loads(Path(args.json_config).expanduser().read_text())
        self.custom_filter, initial = parse_filter_config(config, [])
        self.initial_state = np.asarray(initial, dtype=float)
        self.z_vec = self.initial_state.copy()
        self.prev_time = 0.0
        self.last_input_stamp = None
        self.start_time = None
        self.encoder_value = None
        self.encoder_timestamp = None
        self.combine_data = args.combine_enc_data
        self.filter_publisher = self.create_publisher(StampedFloat64MultiArray, args.out_topic, 10)
        self.create_subscription(StampedFloat64MultiArray, args.inp_value_topic, self.input_value_callback, 10)
        self.create_subscription(StampedFloat64MultiArray, args.inp_encoder_topic, self.encoder_value_callback, 10)
        self.create_subscription(Timekeeper, args.inp_timekeeping_topic, self.timekeeping_callback, 10)

    def timekeeping_callback(self, msg):
        expected = "sim time" if self.get_parameter("use_sim_time").value else "real time"
        if not math.isfinite(msg.start_time) or msg.mode != expected:
            self.start_time = None
            return
        if self.start_time != msg.start_time:
            self._reset(0.0)
            self.last_input_stamp = None
            self.encoder_value = None
            self.encoder_timestamp = None
        self.start_time = msg.start_time

    def _fresh(self, stamp):
        if self.start_time is None or not math.isfinite(stamp):
            return False
        age = self.get_clock().now().nanoseconds * 1e-9 - (self.start_time + stamp)
        return -1e-6 <= age <= INPUT_EXPIRY_SEC

    def encoder_value_callback(self, msg):
        values = np.asarray(msg.data, dtype=float)
        if (self._fresh(msg.timestamp) and values.size and np.isfinite(values).all()
                and (self.encoder_timestamp is None or msg.timestamp > self.encoder_timestamp)):
            self.encoder_value = values
            self.encoder_timestamp = msg.timestamp

    def _reset(self, stamp):
        self.z_vec = self.initial_state.copy()
        self.prev_time = stamp

    def input_value_callback(self, msg):
        stamp = msg.timestamp
        values = np.asarray(msg.data, dtype=float)
        if (not self._fresh(stamp) or not values.size or not np.isfinite(values).all()
                or (self.last_input_stamp is not None and stamp <= self.last_input_stamp)):
            return
        if self.combine_data:
            if self.encoder_value is None or not self._fresh(self.encoder_timestamp):
                return
            values = np.concatenate((values, self.encoder_value))
        self.last_input_stamp = stamp
        if stamp - self.prev_time > INPUT_EXPIRY_SEC:
            self._reset(stamp)
        try:
            # Preserve original pre-step output ordering and controller-facing API.
            output = np.asarray(self.custom_filter.filter_output(self.z_vec, values, stamp)).reshape(-1)
            if not np.isfinite(output).all():
                raise ValueError("nonfinite filter output")
            derivative = self.custom_filter.differential_equation(stamp, self.z_vec, values)
            next_state = advance_filter_state(self.custom_filter, self.prev_time, stamp,
                                              values, self.z_vec, derivative)
        except (ValueError, TypeError, IndexError, ArithmeticError, AssertionError, np.linalg.LinAlgError) as exc:
            self._reset(stamp)
            self.get_logger().warning(f"filter sample dropped; state reset: {exc}")
            return
        self.z_vec = next_state
        self.prev_time = stamp
        message = StampedFloat64MultiArray()
        message.header = "Filter Value"
        message.timestamp = stamp
        message.data = output.astype(float).tolist()
        self.filter_publisher.publish(message)

    def check_filter_valid_state(self, previous_time, current_time, orig_input_val, orig_z_vec, orig_z_vec_dot):
        return advance_filter_state(self.custom_filter, previous_time, current_time,
                                    orig_input_val, orig_z_vec, orig_z_vec_dot)


def main(args=None):
    rclpy.init(args=args)
    node = CustomFilter()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
