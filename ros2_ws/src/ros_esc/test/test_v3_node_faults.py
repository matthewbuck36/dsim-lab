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
def owner(monkeypatch, request):
    assert os.environ.get('ROS_LOCALHOST_ONLY') == '1'
    context = Context()
    rclpy.init(context=context, domain_id=190)
    environment = getattr(request, 'param', 'physical')
    node = runtime.V3Controller(worker=InertWorker(), context=context, parameter_overrides=[
        Parameter('environment', value=environment),
        Parameter('use_sim_time', value=environment == 'gazebo')])
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


@pytest.mark.parametrize('owner', ['physical', 'gazebo'], indirect=True)
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


@pytest.mark.parametrize('owner', ['gazebo'], indirect=True)
def test_controller_defers_sim_clock_lead_without_refreshing_steady_age(owner):
    node, now, steady, commands, _ = owner
    pose(node, 100.01)
    node.observation_callback(observation(100.01, 1))
    node.tick()
    assert node.core.pose is None and node.core.observation is None
    assert commands[-1].linear.x == 0.
    now[0], steady[0] = 100.1, 200.1
    node.tick()
    assert node.core.availability == 'ACTIVE'
    assert node.core.pose.stamp == 100.01
    assert node.core.pose_received == node.core.observation_received == 200.
    assert commands[-1].linear.x > 0.
    steady[0] = 200.51
    node.tick()
    assert node.core.availability == 'WAITING_INPUT'
    assert commands[-1].linear.x == 0.


@pytest.mark.parametrize('owner', ['gazebo'], indirect=True)
def test_controller_clock_catchup_preserves_all_odom_and_expires_buffer(owner):
    node, now, steady, commands, _ = owner
    for stamp in (100.001, 100.034, 100.067):
        pose(node, stamp)
    node.observation_callback(observation(100.001, 1))
    now[0], steady[0] = 100.1, 200.1
    node.tick()
    assert [item.stamp_sec for item in node.core.pose_history] == [100.001, 100.034, 100.067]
    pose(node, 100.11)
    node.observation_callback(observation(100.11, 2))
    steady[0] = 200.7
    node.tick()
    now[0] = 100.2
    node.tick()
    assert node.core.observation.sequence == 1
    assert node.core.pose.stamp == 100.067
    assert commands[-1].linear.x == 0.


@pytest.mark.parametrize('owner', ['gazebo'], indirect=True)
def test_simulated_buffer_does_not_postpone_frame_fault(owner):
    node, now, steady, commands, _ = owner
    start(owner)
    pose(node, 100.01, frame='map')
    node.tick()
    assert node.core.availability == 'FAULTED'
    assert node.core.reason == 'pose_frame_changed'
    assert commands[-1].linear.x == 0.


@pytest.mark.parametrize('owner', ['gazebo'], indirect=True)
def test_simulated_buffer_clears_on_clock_rollback(owner):
    node, now, steady, commands, _ = owner
    node.tick()
    pose(node, 100.01)
    node.observation_callback(observation(100.01, 1))
    now[0] = 99.9
    node.tick()
    assert node.core.reason == 'clock_discontinuity'
    assert node.core.availability == 'FAULTED'
    assert all(not queue.pending for queue in node.delivery.values())
    now[0], steady[0] = 100.1, 200.1
    node.tick()
    assert node.core.observation is None
    assert commands[-1].linear.x == 0.


@pytest.mark.parametrize('owner', ['gazebo'], indirect=True)
def test_deferred_pose_is_evaluated_after_newer_receipt_without_losing_detector_point(owner):
    node, now, steady, _, _ = owner
    start(owner)
    steady[0] = 200.03
    pose(node, 100.03)  # Ahead of /clock100, but first received before the cost below.
    now[0], steady[0] = 100.02, 200.05
    node.observation_callback(observation(100.01, 2))
    assert node.core.observation_received == 200.05
    count = node.core.detector.retained_point_count
    now[0], steady[0] = 100.1, 200.1
    node.tick()
    assert node.core.detector.retained_point_count == count+1
    assert node.core.pose_received == 200.03


@pytest.mark.parametrize('owner', ['gazebo'], indirect=True)
def test_deferred_observation_can_commit_with_pose_received_after_it(owner, monkeypatch):
    node, now, steady, _, _ = owner
    start(owner)
    node.core.begin_candidate((0., 0.), 100., 100.)
    node.core.activity = 'DESIGN'
    node.core.design_started = 100.
    proposal, committed = object(), []
    node.core.ready_proposal = proposal
    def commit(value, stamp):
        committed.append((value, stamp))
        node.core.ready_proposal = None
    monkeypatch.setattr(node.core, '_commit_proposal', commit)
    steady[0] = 200.08
    node.observation_callback(observation(100.08, 2))
    steady[0] = 200.09
    pose(node, 100.09)
    assert not committed
    now[0], steady[0] = 100.1, 200.1
    node._drain_delivery(now[0], steady[0])
    assert committed == [(proposal, 100.1)]
    assert node.core.observation_received == 200.08
    assert node.core.pose_received == 200.09


@pytest.mark.parametrize('owner', ['gazebo'], indirect=True)
def test_distinct_queued_observations_with_shared_receipt_are_both_admitted(owner):
    node, now, steady, _, _ = owner
    start(owner)
    for stamp, sequence, received in ((100.01, 2, 200.01), (100.02, 3, 200.02)):
        steady[0] = received
        message = observation(stamp, sequence)
        set_stamp(message.receipt_stamp, 100.1)
        node.observation_callback(message)
    assert node.core.observation.sequence == 1
    now[0], steady[0] = 100.1, 200.1
    node.tick()
    assert node.core.observation.sequence == 3
    assert node.core.observation.stamp == 100.02
    assert node.core.observation_received == 200.02
    assert 100_010_000_000 in node.core.samples
    assert 100_020_000_000 in node.core.samples
    steady[0] = 200.2
    node.observation_callback(message)  # Duplicate cannot refresh its original receipt.
    assert node.core.observation_received == 200.02


@pytest.mark.parametrize('owner', ['physical', 'gazebo'], indirect=True)
def test_stale_observation_frame_is_discarded_before_integrity_admission(owner):
    node, now, steady, commands, _ = owner
    start(owner)
    now[0], steady[0] = 100.2, 200.2
    message = observation(99., 2)
    message.frame_id = 'map'
    node.observation_callback(message)
    node.tick()
    assert node.core.availability == 'ACTIVE'
    assert node.core.observation.sequence == 1
    assert node.core.observation_received == 200.
    assert commands[-1].linear.x > 0.
