"""Finite callback-level adapter checks; no ROS graph or Gazebo is started."""
from types import SimpleNamespace as NS

import numpy as np
import pytest

pytest.importorskip("rclpy")
pytest.importorskip("ros_esc_interfaces.msg")
from geometry_msgs.msg import Transform
from ros_esc_interfaces.msg import StampedFloat64MultiArray, StampedTransformMultiArray
from ros_esc.encoder_node.encoder_node_script import EncoderNode
from ros_esc.sensor_pose_node.sensor_pose_node_script import SensorPosition
from ros_esc.cost_function_node.cost_function_node_script import CostFunction
from ros_esc.rotate_frame_node.rotate_frame_node_script import RotateFrame


class Publisher:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


def sample(stamp, value=0.0):
    message = StampedFloat64MultiArray()
    message.timestamp = float(stamp)
    message.data = [float(value)]
    return message


def transform_sample(stamp):
    transform = Transform()
    transform.rotation.w = 1.0
    message = StampedTransformMultiArray()
    message.timestamp = float(stamp)
    message.transform_array = [transform]
    return message


def test_joint_source_stamp_survives_encoder_to_sensor():
    encoder_pub, sensor_pub = Publisher(), Publisher()
    encoder = NS(start_time=100.0, joint_names=["arm"], encoder_publisher=encoder_pub)
    joint = NS(name=["arm"], position=[0.25], header=NS(stamp=NS(sec=101, nanosec=250000000)))
    EncoderNode.joint_state_callback(encoder, joint)
    assert encoder_pub.messages[0].timestamp == 1.25
    assert list(encoder_pub.messages[0].data) == [0.25]
    transform_object = NS(transform_output=lambda odom, angle: np.eye(4))
    sensor = NS(start_time=100.0, odom_data=[0, 0, 0, 1, 0, 0, 0], objects_list=[transform_object],
                sensor_pose_publisher=sensor_pub)
    SensorPosition.encoder_callback(sensor, encoder_pub.messages[0])
    assert sensor_pub.messages[0].timestamp == 1.25
    assert sensor_pub.messages[0].transform_array[0].rotation.w == 1.0
    SensorPosition.encoder_callback(sensor, sample(1.3, float("nan")))
    assert len(sensor_pub.messages) == 1


def cost_adapter(period):
    observed = []
    def evaluate(stamp, matrix):
        observed.append((stamp, matrix.copy()))
        return -stamp - 1.0
    return NS(start_time=100.0, sample_period=period, last_published_stamp=None,
              cost_function=NS(cost_output=evaluate), noise_obj=NS(add_noise=lambda stamp, values: values),
              cost_publisher=Publisher(), evaluated=observed)


def test_five_hz_cost_selects_new_transforms_and_preserves_acquisition_stamp():
    adapter = cost_adapter(.2)
    for index in range(31):
        CostFunction.transform_callback(adapter, transform_sample(index / 30))
    messages = adapter.cost_publisher.messages
    np.testing.assert_allclose([message.timestamp for message in messages], np.arange(6) / 5)
    np.testing.assert_allclose([message.data[0] for message in messages], -np.arange(6) / 5 - 1)
    assert len(adapter.evaluated) == 6  # dropped callbacks do not evaluate expensive fields
    CostFunction.transform_callback(adapter, transform_sample(1.0))
    CostFunction.transform_callback(adapter, transform_sample(.8))
    assert len(adapter.cost_publisher.messages) == 6


def test_legacy_unthrottled_cost_still_rejects_duplicate_and_nonfinite_results():
    adapter = cost_adapter(0.0)
    for stamp in (1.0, 1.01, 1.02):
        CostFunction.transform_callback(adapter, transform_sample(stamp))
    assert len(adapter.cost_publisher.messages) == 3
    adapter.cost_function.cost_output = lambda stamp, matrix: float("nan")
    CostFunction.transform_callback(adapter, transform_sample(2.0))
    assert adapter.last_published_stamp == 1.02
    assert len(adapter.cost_publisher.messages) == 3


def test_rotation_final_neutral_is_latched_and_clock_mode_is_explicit():
    publisher, timekeeper = Publisher(), Publisher()
    adapter = NS(stopped=False, start_time=0.0, objects_list=[NS(velocity_output=lambda *args: 2.0)],
                 publishers_list=[publisher], spin_directions=[None],
                 get_clock=lambda: NS(now=lambda: NS(nanoseconds=1000000000)),
                 get_parameter=lambda name: NS(value=False), timekeeper_publisher=timekeeper)
    adapter.stop = lambda: RotateFrame.stop(adapter)
    RotateFrame.encoder_callback(adapter, sample(1.0, .5))
    assert list(publisher.messages[-1].data) == [2.0]
    RotateFrame.stop(adapter)
    RotateFrame.encoder_callback(adapter, sample(1.1, .6))
    assert len(publisher.messages) == 2
    assert list(publisher.messages[-1].data) == [0.0]
    RotateFrame.publish_timekeeper_reading(adapter)
    assert timekeeper.messages[-1].mode == "real time"


def test_nonfinite_spin_profile_neutralizes_instead_of_publishing_nan():
    publisher = Publisher()
    adapter = NS(stopped=False, start_time=0.0, objects_list=[NS(velocity_output=lambda *args: float("nan"))],
                 publishers_list=[publisher], spin_directions=[None],
                 get_clock=lambda: NS(now=lambda: NS(nanoseconds=1000000000)))
    adapter.stop = lambda: RotateFrame.stop(adapter)
    RotateFrame.encoder_callback(adapter, sample(1.0))
    assert adapter.stopped and list(publisher.messages[-1].data) == [0.0]
