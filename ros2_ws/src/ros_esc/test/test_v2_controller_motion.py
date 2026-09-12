"""M3 controller authorization and bounded process shutdown regressions."""

from copy import deepcopy
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import numpy as np
import pytest
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool

from ros_esc.controller_node import controller_node_script as controller
from ros_esc.v2_stream import set_time
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray, Timekeeper

PACKAGE = Path(__file__).parents[1]
CONFIG = PACKAGE / 'ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json'
RUN = 'm3_controller_test'
PREFIX = '/m3_controller_test'
GESC = np.array([.08, 0., 0., 0., 0., .2])
SUPERVISOR = np.array([.05, 0., 0., 0., 0., -.4])


class Recorder:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(deepcopy(message))


def arguments(mode='rolling_gesc_v2'):
    return [PREFIX+'/filter', PREFIX+'/odom', PREFIX+'/timekeeper',
            PREFIX+'/control', PREFIX+'/cmd_vel', str(CONFIG),
            '--algorithm_profile', 'robust_gaussian_v1',
            '--continuous-search-mode', mode, '--v2-run-id', RUN,
            '--algorithm_state_topic', PREFIX+'/state',
            '--supervisor_command_topic', PREFIX+'/supervisor',
            '--startup_timeout_sec', '30']


def state(kind=AlgorithmState.STATE_VERIFY_EXTREMUM, previous=AlgorithmState.STATE_SEARCH, stamp=10.):
    message = AlgorithmState()
    set_time(message.stamp, round(stamp*1e9))
    message.state, message.state_valid = kind, True
    message.previous_state, message.previous_state_valid = previous, True
    message.run_id, message.run_id_valid = RUN, True
    message.algorithm_profile = 'robust_gaussian_v1'
    message.weights_valid = message.failsafe_valid = True
    message.sensor_weight, message.gaussian_weight = 1., 1.
    message.failsafe = kind == AlgorithmState.STATE_FAILSAFE
    return message


def pose(stamp=10.):
    message = Odometry()
    set_time(message.header.stamp, round(stamp*1e9))
    message.header.frame_id, message.pose.pose.orientation.w = 'odom', 1.
    return message


def command():
    message = Twist()
    message.linear.x, message.angular.z = SUPERVISOR[0], SUPERVISOR[5]
    return message


def prepare(node, message=None):
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=0.))
    node.state_callback(pose())
    node.supervisor_command_callback(command())
    node.supervisor_state_callback(message or state())
    node.input_value_callback(StampedFloat64MultiArray(timestamp=10., data=[.08, .04]))


@pytest.fixture
def node_factory(monkeypatch):
    nodes = []
    rclpy.init(args=[])
    def make(mode='rolling_gesc_v2'):
        monkeypatch.setattr(sys, 'argv', ['controller_node', *arguments(mode)])
        node = controller.CustomController()
        node.get_clock().set_ros_time_override(Time(seconds=10))
        for name in ('twist_publisher', 'controller_publisher',
                     'control_diagnostics_publisher', 'algorithm_event_publisher'):
            setattr(node, name, Recorder())
        nodes.append(node)
        return node
    yield make
    for node in nodes:
        node.destroy_node()
    rclpy.try_shutdown()


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
@pytest.mark.parametrize('kind,previous,expected', [
    (AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_RECENTER, GESC+SUPERVISOR),
    (AlgorithmState.STATE_VERIFY_EXTREMUM, AlgorithmState.STATE_SEARCH, GESC),
    (AlgorithmState.STATE_DESIGN_OR_MERGE_FILL, AlgorithmState.STATE_VERIFY_EXTREMUM, GESC),
    (AlgorithmState.STATE_DESIGN_OR_MERGE_FILL, AlgorithmState.STATE_ESCAPE_REPULSE, GESC+SUPERVISOR),
    (AlgorithmState.STATE_DESIGN_OR_MERGE_FILL, AlgorithmState.STATE_SEARCH, np.zeros(6)),
    (AlgorithmState.STATE_ESCAPE_REPULSE, AlgorithmState.STATE_DESIGN_OR_MERGE_FILL, GESC+SUPERVISOR),
    (AlgorithmState.STATE_ESCAPE_ASSIST, AlgorithmState.STATE_DESIGN_OR_MERGE_FILL, GESC+SUPERVISOR),
    (AlgorithmState.STATE_RECENTER, AlgorithmState.STATE_ESCAPE_REPULSE, SUPERVISOR),
    (AlgorithmState.STATE_GOAL_HOLD, AlgorithmState.STATE_VERIFY_EXTREMUM, np.zeros(6)),
    (AlgorithmState.STATE_FAILSAFE, AlgorithmState.STATE_SEARCH, np.zeros(6)),
])
def test_all_three_motion_gates_agree_and_preserve_design_purpose(node_factory, mode, kind, previous, expected):
    node = node_factory(mode)
    if mode == 'stationary_v1' and kind in (2, 3):
        expected = np.zeros(6)
    message = state(kind, previous)
    prepare(node, message)
    assert node._authorized_combination(GESC, SUPERVISOR) == pytest.approx(expected)
    assert node.controller_publisher.messages[-1].data == pytest.approx(node.controller_obj.saturate_command(expected))
    node.twist_publisher.messages.clear()
    node.supervisor_state_callback(message)
    node.watchdog_callback()
    if np.any(expected):
        assert not node.twist_publisher.messages
    else:
        assert len(node.twist_publisher.messages) == 2
        assert all(v.linear.x == v.angular.z == 0 for v in node.twist_publisher.messages)


@pytest.mark.parametrize('kind,expected', [(1, GESC), (2, GESC), (4, GESC+SUPERVISOR), (5, SUPERVISOR), (6, SUPERVISOR)])
def test_enabled_supervisor_owned_assist_keeps_priority(node_factory, kind, expected):
    node = node_factory()
    node.open_field_escape_supervisor_owned_assist_enabled = True
    message = state(kind)
    message.safe_direction_valid = message.safe_direction_revision_valid = True
    message.safe_direction_revision, message.safe_direction_x = 1, 1.
    prepare(node, message)
    assert node._authorized_combination(GESC, SUPERVISOR) == pytest.approx(expected)


@pytest.mark.parametrize('bad', ['run', 'profile', 'state_valid', 'weights', 'failsafe', 'future', 'old', 'rollback', 'design_purpose'])
def test_invalid_selected_state_immediately_stops_all_gates(node_factory, bad):
    node = node_factory()
    prepare(node)
    message = state()
    if bad == 'run':
        message.run_id = 'another_run'
    elif bad == 'profile':
        message.algorithm_profile = 'legacy'
    elif bad == 'state_valid':
        message.state_valid = False
    elif bad == 'weights':
        message.sensor_weight = float('nan')
    elif bad == 'failsafe':
        message.failsafe = True
    elif bad in ('future', 'old', 'rollback'):
        set_time(message.stamp, round({'future':10.51, 'old':9.49, 'rollback':9.99}[bad]*1e9))
    else:
        message.state = AlgorithmState.STATE_DESIGN_OR_MERGE_FILL
        message.previous_state_valid = False
    node.twist_publisher.messages.clear()
    node.supervisor_state_callback(message)
    assert len(node.twist_publisher.messages) == 1
    assert node._authorized_combination(GESC, SUPERVISOR) == pytest.approx(np.zeros(6))
    node.watchdog_callback()
    assert node.twist_publisher.messages[-1].linear.x == 0.


@pytest.mark.parametrize('name', ['supervisor_state_receipt_sec', 'supervisor_command_receipt_sec',
                                 'pose_receipt_sec', 'input_receipt_sec', 'v2_pose_source_ns', 'v2_input_source_ns'])
def test_stale_source_or_receipt_still_forces_zero(node_factory, name):
    node = node_factory()
    prepare(node)
    setattr(node, name, 9. if name.endswith('_sec') else 9_000_000_000)
    node.publish_control_value()
    assert list(node.controller_publisher.messages[-1].data) == [0.]*6
    node.watchdog_callback()
    assert node.twist_publisher.messages[-1].linear.x == 0.


def test_clock_rollback_requires_all_fresh_inputs_and_origin_change_latches(node_factory):
    node = node_factory()
    prepare(node)
    node.get_clock().set_ros_time_override(Time(seconds=9))
    node.watchdog_callback()
    assert node.latest_algorithm_state is None
    assert node.twist_publisher.messages[-1].linear.x == 0.
    node.get_clock().set_ros_time_override(Time(seconds=10))
    node.supervisor_state_callback(state())
    node.publish_control_value()
    assert list(node.controller_publisher.messages[-1].data) == [0.]*6
    prepare(node)
    assert node.controller_publisher.messages[-1].data[0] > 0
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=1.))
    prepare(node)
    assert node.v2_origin_fault and list(node.controller_publisher.messages[-1].data) == [0.]*6


def test_state_receipt_cannot_refresh_stale_source_and_message_copy_is_frozen(node_factory):
    node = node_factory()
    original = state()
    prepare(node, original)
    original.run_id = 'mutated'
    assert node.latest_algorithm_state.run_id == RUN
    node.get_clock().set_ros_time_override(Time(seconds=11))
    node.supervisor_state_callback(state())
    assert not node._motion_authorized(node.latest_algorithm_state)


@pytest.mark.parametrize('source', ['state', 'pose', 'filter'])
def test_source_before_selected_origin_never_authorizes_motion(node_factory, source):
    node = node_factory()
    prepare(node)
    node.v2_origin_ns = 9_900_000_000
    if source == 'state':
        node.v2_last_state_source_ns = None
        node.supervisor_state_callback(state(stamp=9.8))
    elif source == 'pose':
        node.state_callback(pose(9.8))
    else:
        node.input_value_callback(StampedFloat64MultiArray(timestamp=-.1, data=[.08,.04]))
    node.publish_control_value()
    assert list(node.controller_publisher.messages[-1].data) == [0.]*6


@pytest.mark.parametrize('kind,helper,attribute', [
    ('input', 'relative_stamp_ns', 'input_receipt_sec'),
    ('pose', 'time_to_ns', 'pose_receipt_sec'),
    ('command', '_twist_to_six', 'supervisor_command_receipt_sec'),
])
def test_callback_work_does_not_refresh_receipt(node_factory, monkeypatch, kind, helper, attribute):
    node = node_factory()
    prepare(node)
    original = getattr(controller, helper)
    def delayed(*args):
        value = original(*args)
        node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
        return value
    monkeypatch.setattr(controller, helper, delayed)
    if kind == 'input':
        node.input_value_callback(StampedFloat64MultiArray(timestamp=10., data=[.08,.04]))
    elif kind == 'pose':
        node.state_callback(pose())
    else:
        node.supervisor_command_callback(command())
    assert getattr(node, attribute) == 10.


@pytest.mark.parametrize('gate', ['false', 'missing', 'stale'])
def test_wall_recording_gate_preserves_zero_and_no_latching_event(node_factory, monkeypatch, gate):
    node = node_factory()
    prepare(node)
    node.recording_ready_required = True
    node.recording_ready = gate != 'false'
    node.recording_ready_receipt_monotonic = None if gate == 'missing' else 50.
    monkeypatch.setattr(controller.time, 'monotonic', lambda: 51. if gate == 'stale' else 50.)
    node.algorithm_event_publisher.messages.clear()
    node.publish_control_value()
    node.watchdog_callback()
    assert list(node.controller_publisher.messages[-1].data) == [0.]*6
    assert not node.algorithm_event_publisher.messages


def test_post_computation_expiry_and_exception_publish_zero(node_factory, monkeypatch):
    node = node_factory()
    prepare(node)
    original = node.controller_obj.saturate_command
    def late_saturation(values):
        result = original(values)
        node.get_clock().set_ros_time_override(Time(seconds=11))
        return result
    monkeypatch.setattr(node.controller_obj, 'saturate_command', late_saturation)
    node.publish_control_value()
    assert list(node.controller_publisher.messages[-1].data) == [0.]*6
    monkeypatch.setattr(node.controller_obj, 'controller_output', lambda *_: (_ for _ in ()).throw(ValueError('fixture')))
    node.input_value_callback(StampedFloat64MultiArray(timestamp=11., data=[.1, .1]))
    assert node.twist_publisher.messages[-1].linear.x == 0.


@pytest.mark.parametrize('extra', [[], ['--algorithm_profile','legacy'], ['--use-sim-time','False'], ['--v2-run-id','bad run']])
def test_new_mode_requires_explicit_simulation_run_identity(extra):
    argv = arguments()
    if not extra:
        index = argv.index('--v2-run-id')
        del argv[index:index+2]
    with pytest.raises(SystemExit):
        controller.parse_controller_arguments([*argv, *extra])


def test_legacy_parser_default_and_new_flags():
    required = arguments()[:6]
    assert controller.parse_controller_arguments(required).continuous_search_mode == 'stationary_v1'
    assert controller.parse_controller_arguments(arguments()).v2_run_id == RUN


def test_process_sigint_publishes_final_zero_after_moving_verify(tmp_path):
    """Finite real process/DDS fixture; output is isolated and never /cmd_vel."""
    artifact = Path(os.environ.get('DSIM_M3_TEST_ARTIFACT_DIR', str(tmp_path)))
    artifact.mkdir(parents=True, exist_ok=True)
    log = artifact / f'controller_sigint_{time.time_ns()}.log'
    rclpy.init(args=[])
    observer = Node('m3_controller_sigint_observer')
    received = []
    subscription = observer.create_subscription(Twist, PREFIX+'/cmd_vel', received.append, 20)
    publishers = [observer.create_publisher(cls, topic, 20) for cls, topic in (
        (Clock, '/clock'), (Timekeeper, PREFIX+'/timekeeper'), (Odometry, PREFIX+'/odom'),
        (AlgorithmState, PREFIX+'/state'), (Twist, PREFIX+'/supervisor'),
        (Bool, PREFIX+'/ready'), (StampedFloat64MultiArray, PREFIX+'/filter'))]
    process = None
    try:
        with log.open('x') as output:
            process = subprocess.Popen([sys.executable, '-m', controller.__name__, *arguments(),
                                        '--recording_ready_required', 'True', '--recording_ready_topic', PREFIX+'/ready'],
                                       stdout=output, stderr=subprocess.STDOUT)
            deadline = time.monotonic()+20.
            while time.monotonic() < deadline and not any(abs(m.linear.x) > 1e-6 for m in received):
                assert process.poll() is None, log.read_text()
                clock = Clock()
                set_time(clock.clock, 10_000_000_000)
                for publisher, message in zip(publishers, (clock, Timekeeper(mode='sim time', start_time=0.), pose(),
                                                           state(), command(), Bool(data=True),
                                                           StampedFloat64MultiArray(timestamp=10., data=[.08, .04]))):
                    publisher.publish(message)
                rclpy.spin_once(observer, timeout_sec=.02)
            assert any(abs(m.linear.x) > 1e-6 for m in received), f'No moving output; log={log}'
            received.clear()
            process.send_signal(signal.SIGINT)
            deadline = time.monotonic()+5.
            while time.monotonic() < deadline and (process.poll() is None or not received):
                rclpy.spin_once(observer, timeout_sec=.02)
            assert process.wait(timeout=1.) == 0, log.read_text()
            drain_until = time.monotonic()+.25
            while time.monotonic() < drain_until:
                rclpy.spin_once(observer, timeout_sec=.02)
            assert received and received[-1].linear.x == received[-1].angular.z == 0., f'Final zero missing; log={log}'
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2.)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2.)
        observer.destroy_subscription(subscription)
        observer.destroy_node()
        rclpy.try_shutdown()
