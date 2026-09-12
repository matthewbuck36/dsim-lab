"""Q1 policy owner tests; synthetic values do not qualify a neighborhood."""

from dataclasses import replace
from types import SimpleNamespace

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import pytest
import rclpy
from rclpy.node import Node as RosNode
from rclpy.parameter import Parameter
from ros_esc_interfaces.msg import AlgorithmEvent, CostBreakdown, Timekeeper
from std_msgs.msg import Bool

from ros_esc.supervisor_node.state_machine import (
    State, StateMachineConfig, SupervisorStateMachine, TransitionInputs,
)
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor, stamp
from ros_esc.v2_stream import canonical_json
from test_v2_supervisor import (
    Node, Publisher, config as stream_config, confirm, step, stream,
)


FLAG = 'v2_qualification_observation_only'


def machine(**kwargs):
    return SupervisorStateMachine(config=StateMachineConfig(
        moving_verification_enabled=True, qualification_observation_only=True,
        **kwargs))


@pytest.mark.parametrize('confirmed', [False, True])
def test_default_and_explicit_false_preserve_convergence(confirmed):
    assert StateMachineConfig().qualification_observation_only is False
    owner = SupervisorStateMachine(config=StateMachineConfig(
        moving_verification_enabled=True, qualification_observation_only=False))
    first = owner.step(0., TransitionInputs(
        convergence=True, convergence_confirmed=confirmed))
    if confirmed:
        assert first.current == State.VERIFY_EXTREMUM
    else:
        assert first is None
        assert owner.step(2., TransitionInputs(convergence=True)).current == State.VERIFY_EXTREMUM


def test_observation_search_suppresses_direct_and_dwell_confirmation_only():
    owner = machine()
    # An old dwell cannot accumulate while observation is active.
    owner.convergence_started_sec = 0.
    for now in (0., 2., 12., 125.):
        assert owner.step(now, TransitionInputs(
            convergence=True, convergence_confirmed=True)) is None
        assert owner.state == State.SEARCH
        assert owner.weights == (1., 1., 0.)
        assert owner.convergence_started_sec is None


@pytest.mark.parametrize('values,reason', [
    ({'explicit_stop': True}, 'explicit stop'),
    ({'controller_fault': True}, 'controller reported'),
    ({'pose_valid': False}, 'pose invalid'),
    ({'sensor_valid': False}, 'source sample invalid'),
])
def test_observation_keeps_fault_priority_and_failsafe_latch(values, reason):
    owner = machine()
    transition = owner.step(1., TransitionInputs(convergence_confirmed=True, **values))
    assert transition.current == State.FAILSAFE and reason in transition.reason
    assert owner.weights == (0., 0., 0.)
    assert owner.step(2., TransitionInputs(convergence_confirmed=True)) is None
    assert owner.state == State.FAILSAFE


def test_observation_preserves_clock_rollback_fault():
    owner = machine()
    assert owner.step(2.) is None
    transition = owner.step(1., TransitionInputs(convergence_confirmed=True))
    assert transition.current == State.FAILSAFE
    assert 'clock moved backward' in transition.reason


def test_observation_preserves_bounded_recovery_and_its_timeout():
    owner = machine(recoverable_navigation_enabled=True, recovery_retry_limit=1)
    transition = owner.step(1., TransitionInputs(
        convergence_confirmed=True, recenter_recovery_requested=True))
    assert transition.current == State.RECENTER
    assert owner.recovery_retry_count == 1
    transition = owner.step(31.1, TransitionInputs(convergence_confirmed=True))
    assert transition.current == State.FAILSAFE


@pytest.mark.parametrize('bad', [0, 1, 'true', None])
def test_policy_config_is_strict_boolean(bad):
    with pytest.raises(ValueError, match='must be boolean'):
        StateMachineConfig(moving_verification_enabled=True,
                           qualification_observation_only=bad)


def test_policy_config_requires_moving_mode():
    with pytest.raises(ValueError, match='requires moving verification'):
        StateMachineConfig(qualification_observation_only=True)


@pytest.mark.parametrize('mode', ['pde_mean_v1', 'centroid_windows_v2'])
@pytest.mark.parametrize('known', [1, 2])
def test_both_valid_confirmation_kinds_observe_without_consuming_lifecycle(monkeypatch, mode, known):
    # Fix wall time only in this detached fixture; actual node tests use the
    # real clock. The control proves that missing evidence cannot explain Q1.
    monkeypatch.setattr('ros_esc.supervisor_node.v2_supervisor.time.monotonic_ns',
                        lambda: 1_000_000_000)
    for enabled in (False, True):
        node = Node(known)
        node.machine.config = replace(node.machine.config,
                                      qualification_observation_only=enabled)
        owner = MovingSupervisor(node, stream_config(), .75, .15)
        node.adapter = owner
        clock = Timekeeper(); clock.mode = 'sim time'; clock.start_time = 0.
        owner.timekeeper(clock)
        owner.readiness(Bool(data=True))
        stream(owner)
        evidence = owner.raw.evaluate((0., 0.), .75, .15, owner.now())
        assert evidence.ready and evidence.informative
        confirmation = confirm(owner, mode)
        if not enabled:
            assert step(owner).current == State.VERIFY_EXTREMUM
            target = State.GOAL_HOLD if known == 1 else State.DESIGN_OR_MERGE_FILL
            assert step(owner).current == target
            continue
        for _ in range(3):
            owner.confirmation(confirmation)
            assert step(owner) is None
            owner.publish_context()
        assert node.machine.state == State.SEARCH and node.machine.weights == (1., 1., 0.)
        assert owner.epoch == 1 and owner.accepted_epoch is None
        assert owner.candidate is None and owner.current_preparation is None
        assert (owner.candidate_sequence, owner.preparation_sequence, owner.command_sequence) == (0, 0, 0)
        assert not owner.preparations and not owner.published_snapshots
        assert not owner.command_publisher.messages and not owner.snapshot_publisher.messages
        contexts = owner.epoch_publisher.messages
        assert len(contexts) >= 4 and all(m.valid and m.search_epoch == 1 for m in contexts)
        assert [m.context_sequence for m in contexts] == sorted({m.context_sequence for m in contexts})
        assert not node.machine.filled_candidate_costs and node.machine.active_fill_count == 0


@pytest.fixture
def ros_context():
    rclpy.init(args=[])
    try:
        yield
    finally:
        rclpy.try_shutdown()


def parameters(**overrides):
    values = dict(use_sim_time=True, continuous_search_mode='rolling_gesc_v2',
                  v2_run_id='q1_policy_fixture',
                  v2_stream_config_json=canonical_json(stream_config()),
                  extremum_classification_mode='counted_candidates',
                  known_source_count=2, max_fill_clusters=1,
                  v2_candidate_radius_m=.75, v2_candidate_epsilon_m=.15,
                  v2_qualification_observation_only=True,
                  recording_ready_required=True)
    values.update(overrides)
    return [Parameter(name, value=value) for name, value in values.items()]


@pytest.mark.parametrize('overrides,reason', [
    ({'continuous_search_mode': 'stationary_v1'}, 'requires moving verification'),
    ({'algorithm_profile': 'legacy'}, 'only valid for algorithm_profile'),
    ({'use_sim_time': False}, 'requires robust_gaussian_v1 simulation'),
    ({'v2_candidate_radius_m': 0.}, 'explicit positive finite'),
    ({'v2_candidate_epsilon_m': 0.}, 'explicit positive finite'),
])
def test_actual_startup_scope_and_positive_neighborhood_remain_required(ros_context, overrides, reason):
    # Capture a partially initialized node so rejected startup leaves no ROS
    # entities behind in the test process.
    node = SupervisorNode.__new__(SupervisorNode)
    try:
        with pytest.raises(ValueError, match=reason):
            node.__init__(parameter_overrides=parameters(**overrides))
    finally:
        RosNode.destroy_node(node)


@pytest.mark.parametrize('mode', ['pde_mean_v1', 'centroid_windows_v2'])
def test_actual_callback_policy_configuration_heartbeat_stop_and_shutdown(ros_context, monkeypatch, mode):
    node = SupervisorNode(parameter_overrides=parameters())
    commands, states, events = Publisher(), Publisher(), Publisher()
    node.command_publisher, node.state_publisher, node.event_publisher = commands, states, events
    owner = node.moving_v2
    owner.command_publisher = Publisher()
    owner.snapshot_publisher = Publisher()
    owner.epoch_publisher = Publisher()
    now = [1_000_000_000]
    monkeypatch.setattr(node, 'get_clock', lambda: SimpleNamespace(
        now=lambda: SimpleNamespace(nanoseconds=now[0], to_msg=lambda: stamp(now[0]))))
    try:
        assert node.describe_parameter(FLAG).read_only
        result = node.set_parameters([Parameter(FLAG, value=False)])[0]
        assert not result.successful and node.get_parameter(FLAG).value is True
        clock = Timekeeper(); clock.mode = 'sim time'; clock.start_time = 0.
        owner.timekeeper(clock)
        owner.readiness(Bool(data=True))
        for _ in range(3):
            pose = Odometry(); pose.header.frame_id = 'odom'; pose.header.stamp = stamp(now[0])
            pose.pose.pose.orientation.w = 1.
            node.pose_callback(pose)
            raw = CostBreakdown(); raw.source_timestamp = now[0] * 1e-9
            raw.source_timestamp_valid = raw.raw_cost_valid = True
            raw.channel_count = 1; raw.raw_cost = [-1.]
            node.source_callback(raw)
            confirm(owner, mode)
            node.timer_callback()
            assert node.machine.state == State.SEARCH
            now[0] += 50_000_000
        assert len(states.messages) == 3 and all(m.state == int(State.SEARCH) for m in states.messages)
        assert all(m.valid for m in owner.epoch_publisher.messages)
        config_events = [m for m in events.messages if FLAG in m.value_names]
        assert len(config_events) == 1
        event = config_events[0]
        assert event.event_type == AlgorithmEvent.EVENT_CONFIGURATION
        assert dict(zip(event.value_names, event.values))[FLAG] == 1.
        assert not owner.command_publisher.messages and not owner.snapshot_publisher.messages
        assert owner.candidate_sequence == 0 and owner.accepted_epoch is None
        node.stop_callback(Bool(data=True))
        node.timer_callback()
        assert node.machine.state == State.FAILSAFE and states.messages[-1].state == int(State.FAILSAFE)
        assert commands.messages[-1] == Twist()
        # Shutdown must issue an explicit final zero even after a nonzero
        # previously published command; no controller or cmd_vel owner bypass.
        previous = Twist(); previous.linear.x = .1
        commands.publish(previous)
    finally:
        node.destroy_node()
    assert commands.messages[-2].linear.x == .1 and commands.messages[-1] == Twist()
