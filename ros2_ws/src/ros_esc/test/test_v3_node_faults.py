"""V3 ROS boundary fault isolation on an isolated local DDS domain."""

import math
import os
import time
from types import SimpleNamespace

import numpy as np
import pytest
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.context import Context
from rclpy.node import Node
from rclpy.parameter import Parameter
from ros_esc_interfaces.msg import SensorObservation, Timekeeper

from ros_esc.gesc_v3 import node as runtime
from ros_esc.gesc_v3.observation_node import set_stamp


class InertWorker:
    def poll(self):
        return None
    def submit(self, *_args, **_kwargs):
        return False
    def close(self):
        pass


@pytest.fixture
def owner(monkeypatch):
    assert os.environ.get('ROS_LOCALHOST_ONLY') == '1'
    context = Context()
    rclpy.init(context=context, domain_id=190)
    node = runtime.V3Controller(worker=InertWorker(), context=context, parameter_overrides=[
        Parameter('environment', value='physical'), Parameter('use_sim_time', value=False)])
    now, steady, commands = [100.], [200.], []
    node.get_clock = lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=round(now[0] * 1e9)))
    monkeypatch.setattr(runtime.time, 'monotonic', lambda: steady[0])
    node.command_publisher = SimpleNamespace(publish=commands.append)
    node.timekeeper_callback(Timekeeper(mode='real time', start_time=99.))
    try:
        yield node, now, steady, commands, context
    finally:
        node.stop()
        node.destroy_node()
        context.try_shutdown()


def pose(node, stamp, frame='odom'):
    message = Odometry()
    set_stamp(message.header.stamp, stamp)
    message.header.frame_id = frame
    message.pose.pose.orientation.w = 1.
    node.pose_callback(message)


def observation(stamp, sequence):
    message = SensorObservation(source_instance='fault_test_sensor', sequence=sequence,
        timestamp_basis=SensorObservation.RECEIPT_TIME, frame_id='odom', raw_cost=-2.,
        sensor_x_m=.18, valid=True, acquisition_uncertainty_sec=math.nan)
    set_stamp(message.stamp, stamp)
    set_stamp(message.receipt_stamp, stamp)
    return message


def start(owner):
    node, now, _, commands, _ = owner
    pose(node, now[0])
    node.observation_callback(observation(now[0], 1))
    node.tick()
    assert node.core.availability == 'ACTIVE' and commands[-1].linear.x > 0


def unavailable(_message):
    raise RuntimeError('injected optional publication failure')


@pytest.mark.parametrize('publisher', ['filter_publisher', 'control_publisher', 'event_publisher', 'fill_publisher'])
def test_optional_publication_failure_cannot_fault_fresh_control(owner, publisher):
    node, now, steady, commands, _ = owner
    start(owner)
    setattr(node, publisher, SimpleNamespace(publish=unavailable))
    now[0], steady[0] = 100.2, 200.2
    pose(node, now[0])
    node.observation_callback(observation(now[0], 2))
    node.core.emit(now[0], 'optional_test', 'event for failure injection')
    node.core.fill_events.append(SimpleNamespace(
        source_timestamp=now[0], fill_id=1, cluster_id=1, revision=1,
        amplitude=1., sigma_major=.2, sigma_minor=.1, orientation=0.,
        support_radius=.4, exit_radius=.5, confidence=.8, sample_count=20,
        fit_residual=0., fit_condition_number=1., design_escalations=0,
        active=True, superseded=False, center=np.zeros(2), covariance=np.eye(2),
        fit_condition_number_valid=True))
    node.tick()
    assert node.core.availability == 'ACTIVE'
    assert node.core.observation.sequence == 2
    assert commands[-1].linear.x > 0


@pytest.mark.parametrize('invalid', ['flag', 'future', 'nonfinite', 'basis', 'timestamp', 'empty_frame'])
def test_invalid_observation_never_renews_last_good_input(owner, invalid):
    node, now, steady, commands, _ = owner
    start(owner)
    now[0], steady[0] = 100.4, 200.4
    message = observation(now[0], 2)
    if invalid == 'flag':
        message.valid, message.reason = False, 'missing_phase_support'
    elif invalid == 'future':
        set_stamp(message.stamp, 101.)
    elif invalid == 'nonfinite':
        message.raw_cost = math.nan
    elif invalid == 'basis':
        message.timestamp_basis = 255
    elif invalid == 'timestamp':
        message.stamp.nanosec = 1_000_000_000
    else:
        message.frame_id = ''
    node.observation_callback(message)
    assert node.core.observation.sequence == 1
    assert node.core.observation_received == 200.
    now[0], steady[0] = 100.6, 200.6
    pose(node, now[0])
    node.tick()
    assert node.core.availability == 'WAITING_INPUT'
    assert commands[-1].linear.x == 0.


def test_changed_observation_frame_faults_control(owner):
    node, now, steady, commands, _ = owner
    start(owner)
    now[0], steady[0] = 100.2, 200.2
    message = observation(now[0], 2)
    message.frame_id = 'map'
    node.observation_callback(message)
    node.tick()
    assert node.core.availability == 'FAULTED'
    assert node.core.reason == 'observation_frame_conflict'
    assert commands[-1].linear.x == 0.


def test_actual_competing_command_publisher_faults_control(owner):
    node, _, _, commands, context = owner
    start(owner)
    competitor = Node('unintended_command_owner', context=context)
    competitor.create_publisher(Twist, '/cmd_vel', 10)
    try:
        # Both are in one process/context; publisher discovery is still DDS.
        for _ in range(100):
            if node.count_publishers('/cmd_vel') > 1:
                break
            time.sleep(.01)
        assert node.count_publishers('/cmd_vel') > 1
        node.check_ownership()
        node.tick()
        assert node.core.availability == 'FAULTED'
        assert node.core.reason == 'multiple_command_publishers'
        assert commands[-1].linear.x == 0.
    finally:
        competitor.destroy_node()


def test_graph_metadata_unavailable_is_not_motion_authority(owner, monkeypatch):
    node, _, _, commands, _ = owner
    start(owner)
    def unavailable_count(_topic):
        raise RuntimeError('graph query unavailable')
    monkeypatch.setattr(node, 'count_publishers', unavailable_count)
    node.check_ownership()
    node.tick()
    assert node.core.availability == 'ACTIVE' and commands[-1].linear.x > 0


def test_optional_filter_formatting_exception_cannot_unwind_control(owner, monkeypatch):
    node, now, steady, commands, _ = owner
    start(owner)
    now[0], steady[0] = 100.2, 200.2
    pose(node, now[0])
    original_evaluate = node.core.rolling.evaluate
    def unavailable_format(*_args, **_kwargs):
        raise ValueError('injected optional filter formatting failure')
    monkeypatch.setattr(node.core.rolling, 'evaluate', unavailable_format)
    node.observation_callback(observation(now[0], 2))
    monkeypatch.setattr(node.core.rolling, 'evaluate', original_evaluate)
    node.tick()
    assert node.core.availability == 'ACTIVE'
    assert commands[-1].linear.x > 0
