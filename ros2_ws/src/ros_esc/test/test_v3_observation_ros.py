"""ROS message boundary tests using observed support and no physical devices."""

import math
from types import SimpleNamespace

import pytest

from ros_esc.gesc_v3.observation_node import SensorObservationNode, pose_from_message, seconds, set_stamp


def test_stamp_and_pose_conversion_preserve_observed_frame():
    from builtin_interfaces.msg import Time
    from nav_msgs.msg import Odometry
    stamp = Time()
    set_stamp(stamp, 23.125)
    assert seconds(stamp) == 23.125
    with pytest.raises(ValueError):
        set_stamp(stamp, math.inf)
    pose = Odometry()
    pose.header.frame_id = 'odom'
    pose.header.stamp = stamp
    pose.pose.pose.position.x = 1.25
    pose.pose.pose.orientation.w = math.cos(.25)
    pose.pose.pose.orientation.z = math.sin(.25)
    result = pose_from_message(pose)
    assert result.frame == 'odom' and result.x == 1.25
    assert result.yaw == pytest.approx(.5)
    pose.header.frame_id = ''
    with pytest.raises(ValueError):
        pose_from_message(pose)


@pytest.fixture
def adapter(request):
    import rclpy
    from rclpy.context import Context
    from rclpy.parameter import Parameter
    messages = pytest.importorskip('ros_esc_interfaces.msg')
    if not hasattr(messages, 'SensorObservation'):
        pytest.skip('build the eight-interface V3 package before ROS adapter tests')
    context = Context()
    rclpy.init(context=context, domain_id=188)
    environment = getattr(request, 'param', 'physical')
    node = SensorObservationNode(context=context, parameter_overrides=[
        Parameter('environment', value=environment),
        Parameter('use_sim_time', value=environment == 'gazebo')])
    output = []
    node.publisher = SimpleNamespace(publish=output.append)
    now = [100.]
    node.get_clock = lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=round(now[0] * 1e9)))
    try:
        yield node, now, output, messages
    finally:
        node.destroy_node()
        context.try_shutdown()


def send_pose(node, stamp, x=0., y=0., yaw=0., frame='odom'):
    from nav_msgs.msg import Odometry
    message = Odometry()
    set_stamp(message.header.stamp, stamp)
    message.header.frame_id = frame
    message.pose.pose.position.x, message.pose.pose.position.y = x, y
    message.pose.pose.orientation.z = math.sin(yaw / 2)
    message.pose.pose.orientation.w = math.cos(yaw / 2)
    node.pose_callback(message)


def test_nearby_support_produces_one_measured_observation_without_full_rotation(adapter):
    node, now, output, messages = adapter
    node.timekeeper_callback(messages.Timekeeper(mode='real time', start_time=99.))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=1., data=[-2.]))
    assert not any(message.valid for message in output)
    send_pose(node, 100., x=1., y=2., yaw=math.pi / 2)
    node.phase_callback(messages.StampedFloat64MultiArray(timestamp=1., data=[0.]))
    valid = [message for message in output if message.valid]
    assert len(valid) == 1
    sample = valid[0]
    assert sample.raw_cost == -2.
    assert sample.sensor_x_m == pytest.approx(1.)
    assert sample.sensor_y_m == pytest.approx(2.18)
    assert seconds(sample.stamp) == 100. and seconds(sample.receipt_stamp) == 100.
    assert sample.timestamp_basis == sample.RECEIPT_TIME
    assert math.isnan(sample.acquisition_uncertainty_sec)
    assert sample.device_sequence_valid is False
    assert sample.phase_rad == 0.  # No duplicate physical encoder offset.
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=1., data=[-9.]))
    node.poll()
    assert len([message for message in output if message.valid]) == 1
    assert '/cmd_vel' not in [publisher.topic_name for publisher in node.publishers]


def test_expired_sample_drops_and_fresh_sample_recovers(adapter):
    node, now, output, messages = adapter
    node.timekeeper_callback(messages.Timekeeper(mode='real time', start_time=99.))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=1., data=[-2.]))
    now[0] = 100.6
    node.poll()
    assert output[-1].valid is False and output[-1].reason == 'sample_expired_or_future'
    send_pose(node, 100.6)
    node.phase_callback(messages.StampedFloat64MultiArray(timestamp=1.6, data=[.2]))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=1.6, data=[-3.]))
    assert output[-1].valid is True and output[-1].raw_cost == -3.
    assert output[-1].sequence == 2
    assert node.fault is None


@pytest.mark.parametrize('fault', ['time_origin_changed', 'clock_discontinuity', 'pose_frame_changed'])
@pytest.mark.parametrize('adapter', ['physical', 'gazebo'], indirect=True)
def test_integrity_fault_is_reported_and_never_silently_remapped(adapter, fault):
    node, now, output, messages = adapter
    node.timekeeper_callback(messages.Timekeeper(mode=node.expected_mode, start_time=99.))
    if fault == 'time_origin_changed':
        node.timekeeper_callback(messages.Timekeeper(mode=node.expected_mode, start_time=99.1))
    elif fault == 'clock_discontinuity':
        now[0] = 98.
        node.poll()
    else:
        send_pose(node, 100., frame='map')
    assert node.fault == fault
    assert output[-1].reason == fault and output[-1].valid is False
    now[0] = 101.
    node.timekeeper_callback(messages.Timekeeper(mode=node.expected_mode, start_time=99.))
    send_pose(node, 101.)
    node.phase_callback(messages.StampedFloat64MultiArray(timestamp=2., data=[0.]))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=2., data=[-2.]))
    assert not any(message.valid for message in output)


def test_initial_timekeeper_can_precede_clock_delivery(adapter):
    node, now, output, messages = adapter
    now[0] = 0.
    node.timekeeper_callback(messages.Timekeeper(mode='real time', start_time=99.))
    assert node.origin == 99. and node.fault is None


@pytest.mark.parametrize('adapter', ['gazebo'], indirect=True)
def test_simulated_clock_lead_waits_then_preserves_actual_observation(adapter, monkeypatch):
    from ros_esc.gesc_v3 import observation_node as runtime
    node, now, output, messages = adapter
    steady = [200.]
    monkeypatch.setattr(runtime, 'time', SimpleNamespace(monotonic=lambda: steady[0]))
    now[0] = 45.9
    node.timekeeper_callback(messages.Timekeeper(mode='sim time', start_time=40.))
    send_pose(node, 45.901, x=1.)
    node.phase_callback(messages.StampedFloat64MultiArray(timestamp=5.901, data=[.2]))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=5.901, data=[-2.]))
    node.poll()
    assert not output
    assert node.builder.sequence == 0
    now[0], steady[0] = 45.95, 200.05
    node.poll()
    valid = [message for message in output if message.valid]
    assert len(valid) == 1
    assert seconds(valid[0].stamp) == pytest.approx(45.901)
    assert seconds(valid[0].receipt_stamp) == pytest.approx(45.9)
    assert valid[0].source_pose.x == 1.
    assert valid[0].phase_rad == pytest.approx(.2)
    assert valid[0].timestamp_basis == valid[0].ESTIMATED_TIME
    node.poll()
    assert len([message for message in output if message.valid]) == 1


@pytest.mark.parametrize('adapter', ['gazebo'], indirect=True)
def test_frozen_sim_clock_cannot_revive_old_buffered_cost(adapter, monkeypatch):
    from ros_esc.gesc_v3 import observation_node as runtime
    node, now, output, messages = adapter
    steady = [200.]
    monkeypatch.setattr(runtime, 'time', SimpleNamespace(monotonic=lambda: steady[0]))
    node.timekeeper_callback(messages.Timekeeper(mode='sim time', start_time=99.))
    send_pose(node, 100.01)
    node.phase_callback(messages.StampedFloat64MultiArray(timestamp=1.01, data=[.2]))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=1.01, data=[-2.]))
    steady[0] = 200.6
    node.poll()
    now[0] = 100.1
    node.poll()
    assert not any(message.valid for message in output)
    assert node.builder.sequence == 0


def test_physical_future_input_is_rejected_without_buffering(adapter):
    node, now, output, messages = adapter
    node.timekeeper_callback(messages.Timekeeper(mode='real time', start_time=99.))
    send_pose(node, 100.01)
    node.phase_callback(messages.StampedFloat64MultiArray(timestamp=1.01, data=[.2]))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=1.01, data=[-2.]))
    now[0] = 100.1
    node.poll()
    assert node.delivery is None
    assert not any(message.valid for message in output)


@pytest.mark.parametrize('adapter', ['gazebo'], indirect=True)
def test_released_cost_waiting_support_keeps_original_steady_expiry(adapter, monkeypatch):
    from ros_esc.gesc_v3 import observation_node as runtime
    node, now, output, messages = adapter
    steady = [200.]
    monkeypatch.setattr(runtime, 'time', SimpleNamespace(monotonic=lambda: steady[0]))
    node.timekeeper_callback(messages.Timekeeper(mode='sim time', start_time=99.))
    node.cost_callback(messages.StampedFloat64MultiArray(timestamp=1.01, data=[-2.]))
    now[0], steady[0] = 100.1, 200.1
    node.poll()
    assert node.builder.pending is not None
    assert node.pending_steady == 200.
    steady[0] = 200.6
    send_pose(node, 100.01)
    node.phase_callback(messages.StampedFloat64MultiArray(timestamp=1.01, data=[.2]))
    node.poll()
    assert node.builder.pending is None
    assert not any(message.valid for message in output)
