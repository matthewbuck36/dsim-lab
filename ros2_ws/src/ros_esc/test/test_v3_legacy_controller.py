"""Original controller compatibility and bounded command admission."""

import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest
from rclpy.clock import ClockType
from rclpy.context import Context
from ros_esc_interfaces.msg import StampedFloat64MultiArray, Timekeeper

from ros_esc.controller_node import controller_node_script as runtime
from ros_esc.config_parsing import parse_object_config


ARGV = ['/filter', '/odom', '/timekeeper', '/control', '/cmd_vel', '/unused.json', '--use-sim-time', 'False']


@pytest.fixture
def controller(monkeypatch):
    import rclpy
    context = Context()
    rclpy.init(context=context, domain_id=187)
    calls = []
    def output(stamp, state, values):
        calls.append((stamp, state.copy(), values.copy()))
        return [float(values[0]), 0., 0., 0., 0., float(values[1])]
    node = runtime.CustomController(ARGV, controller_obj=SimpleNamespace(controller_output=output), context=context)
    commands, diagnostic = [], []
    node.twist_publisher = SimpleNamespace(publish=commands.append)
    node.controller_publisher = SimpleNamespace(publish=diagnostic.append)
    selected_now, steady_now = [100.], [200.]
    node.get_clock = lambda: SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=round(selected_now[0] * 1e9)))
    monkeypatch.setattr(runtime.time, 'monotonic', lambda: steady_now[0])
    node.timekeeping_callback(Timekeeper(mode='real time', start_time=99.))
    try:
        yield node, selected_now, steady_now, commands, diagnostic, calls
    finally:
        node.stop()
        node.destroy_node()
        context.try_shutdown()


def pose(node, stamp, frame='odom', x=1., yaw=.3):
    from nav_msgs.msg import Odometry
    message = Odometry()
    message.header.frame_id = frame
    ns = round(stamp * 1e9)
    message.header.stamp.sec, message.header.stamp.nanosec = divmod(ns, 1_000_000_000)
    message.pose.pose.position.x = x
    message.pose.pose.orientation.z = math.sin(yaw / 2)
    message.pose.pose.orientation.w = math.cos(yaw / 2)
    node.state_callback(message)


def sample(node, stamp, values=(.04, .2)):
    node.input_value_callback(StampedFloat64MultiArray(timestamp=stamp, data=list(values)))


def test_first_fresh_direction_starts_and_old_receipts_expire_with_held_clock(controller):
    node, now, steady, commands, diagnostic, calls = controller
    sample(node, 1.)
    assert node.availability == 'WAITING_INPUT'
    pose(node, 100.)
    assert node.availability == 'ACTIVE' and commands[-1].linear.x == .04
    assert calls[0][0] == 1.
    np.testing.assert_allclose(calls[0][1], [1., 0., 0., 0., 0., .3])
    assert list(diagnostic[-1].data) == [0.04, 0., 0., 0., 0., .2]
    assert node.watchdog_timer.clock.clock_type == ClockType.STEADY_TIME
    node.watchdog_callback()
    assert len(calls) == 1  # No repeated numerical integration of one sample.
    steady[0] = 200.6
    sample(node, 1.)  # Duplicate delivery cannot refresh the receipt age.
    pose(node, 100.)
    node.watchdog_callback()
    assert node.availability == 'WAITING_INPUT' and commands[-1].linear.x == 0.
    now[0], steady[0] = 100.6, 200.6
    pose(node, 100.6)
    sample(node, 1.6)
    assert node.availability == 'ACTIVE' and commands[-1].linear.x == .04
    assert len(calls) == 2
    assert sorted(subscription.topic_name for subscription in node.subscriptions) == ['/filter', '/odom', '/timekeeper']


def test_invalid_inputs_never_refresh_and_operator_stop_never_recovers(controller):
    node, now, steady, commands, diagnostic, calls = controller
    pose(node, 100.)
    sample(node, 1.)
    now[0], steady[0] = 100.6, 200.6
    sample(node, 1.6, (math.nan, .2))
    pose(node, 100.6, x=math.inf)
    sample(node, 3.)  # Future input is also unusable.
    node.watchdog_callback()
    assert node.availability == 'WAITING_INPUT'
    assert node.input_stamp == 100. and node.pose_stamp == 100.
    node.stop()
    pose(node, 100.6)
    sample(node, 1.6)
    assert node.availability == 'STOPPED' and commands[-1].linear.x == 0.
    assert list(diagnostic[-1].data) == [0.] * 6
    assert len(calls) == 1


@pytest.mark.parametrize('change', ['origin', 'clock', 'frame'])
def test_integrity_change_latches_fault(controller, change):
    node, now, steady, commands, _, _ = controller
    pose(node, 100.)
    sample(node, 1.)
    if change == 'origin':
        node.timekeeping_callback(Timekeeper(mode='real time', start_time=99.1))
    elif change == 'clock':
        now[0] = 99.
        node.watchdog_callback()
    else:
        pose(node, 100.1, frame='map')
    assert node.availability == 'FAULTED' and commands[-1].linear.x == 0.
    now[0], steady[0] = 100.2, 200.2
    pose(node, 100.2)
    sample(node, 1.2)
    assert node.availability == 'FAULTED' and commands[-1].linear.x == 0.


def test_nonfinite_output_faults_before_any_bad_twist(controller):
    node, _, _, commands, _, _ = controller
    node.controller_obj = SimpleNamespace(controller_output=lambda *args: [math.nan] * 6)
    pose(node, 100.)
    sample(node, 1.)
    assert node.availability == 'FAULTED'
    assert all(math.isfinite(message.linear.x) and message.linear.x == 0. for message in commands)


def test_output_that_finishes_after_input_expiry_is_not_published(controller):
    node, _, steady, commands, _, _ = controller
    def delayed_output(*_args):
        steady[0] += .6
        return [.04, 0., 0., 0., 0., .2]
    node.controller_obj = SimpleNamespace(controller_output=delayed_output)
    pose(node, 100.)
    sample(node, 1.)
    assert node.availability == 'WAITING_INPUT'
    assert all(message.linear.x == 0. for message in commands)


def test_original_lie_bracket_scalar_formula_remains_available(controller):
    node, _, _, commands, _, _ = controller
    config_path = Path(__file__).parents[1] / 'config/profiles/assets/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/lie_bracket_controller_voltage.json'
    config = json.loads(config_path.read_text())
    node.controller_obj = parse_object_config(config)
    expected = parse_object_config(config).controller_output(1., np.zeros(6), .01)
    pose(node, 100.)
    sample(node, 1., (.01, .4))  # Inherited recipe includes a filtered encoder.
    assert node.availability == 'ACTIVE'
    assert abs(expected[5]) < node.controller_obj.max_wz  # Exercise the unclipped scalar law.
    assert commands[-1].linear.x == expected[0]
    assert commands[-1].angular.z == expected[5]


def test_small_cli_and_v3_dispatch_preserve_ros_arguments(monkeypatch):
    assert runtime.parse_controller_arguments(ARGV).use_sim_time is False
    with pytest.raises(SystemExit):
        runtime.parse_controller_arguments(ARGV + ['--recording_ready_required', 'True'])
    with pytest.raises(SystemExit):
        runtime.parse_controller_arguments(ARGV[:-1] + ['tru'])
    seen = []
    monkeypatch.setitem(sys.modules, 'ros_esc.gesc_v3.node', SimpleNamespace(main=lambda args: seen.append(args)))
    runtime.main(['--v3', '--ros-args', '-p', 'environment:=gazebo'])
    assert seen == [['--ros-args', '-p', 'environment:=gazebo']]


@pytest.mark.parametrize('signum', [2, 15])
def test_process_signal_waits_for_callback_then_final_zero_before_context_shutdown(monkeypatch, signum):
    import os
    import signal
    events, live = [], [False]
    class Node:
        def __init__(self, _args):
            events.append('created')
        def stop(self):
            assert live[0]
            events.append('final zero')
        def destroy_node(self):
            events.append('destroyed')
    class Executor:
        def add_node(self, _node):
            pass
        def spin_once(self, timeout_sec):
            os.kill(os.getpid(), signum)
            events.append('callback finished')
        def shutdown(self, timeout_sec):
            events.append('executor stopped')
    monkeypatch.setattr(runtime, 'CustomController', Node)
    monkeypatch.setattr(runtime, 'SingleThreadedExecutor', Executor)
    monkeypatch.setattr(runtime.rclpy, 'init', lambda **_kwargs: live.__setitem__(0, True))
    monkeypatch.setattr(runtime.rclpy, 'ok', lambda: live[0])
    def shutdown():
        live[0] = False
        events.append('context stopped')
    monkeypatch.setattr(runtime.rclpy, 'try_shutdown', shutdown)
    previous = signal.getsignal(signum)
    runtime.main(ARGV)
    assert events == ['created', 'callback finished', 'final zero', 'executor stopped', 'destroyed', 'context stopped']
    assert signal.getsignal(signum) == previous
