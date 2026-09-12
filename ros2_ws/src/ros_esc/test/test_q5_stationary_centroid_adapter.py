"""Independent actual-owner tests for detector-only stationary Arm B."""

from copy import deepcopy
from types import SimpleNamespace

import pytest
import rclpy
from rclpy.parameter import Parameter
from rclpy.time import Time
from std_msgs.msg import Bool
from ros_esc.supervisor_node.state_machine import State, SupervisorStateMachine, TransitionInputs
from ros_esc.controller_node.controller_node_script import CustomController
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc_interfaces.msg import AlgorithmEvent, CentroidConvergenceDiagnostics, Timekeeper
from ros_esc.v2_stream import set_time, time_to_ns
from test_q5_stationary_fill_protocol import ORIGIN_NS, confirmation
from test_supervisor_integration import Recorder, _confirmed_convergence, _convergence, _pose, _source


def test_arm_b_has_authoritative_typed_centroid_subscription():
    rclpy.init()
    node = None
    try:
        node = SupervisorNode(parameter_overrides=[
            Parameter('algorithm_profile', value='robust_gaussian_v1'),
            Parameter('continuous_search_mode', value='stationary_v1'),
            Parameter('convergence_metric_mode', value='centroid_windows_v2'),
            Parameter('use_sim_time', value=True),
        ])
        subscriptions = [(subscription.topic_name, subscription.msg_type)
                         for subscription in node.subscriptions]
        assert (
            '/gesc_gaussian/v2/convergence_diagnostics',
            CentroidConvergenceDiagnostics,
        ) in subscriptions, subscriptions
        assert node.moving_v2 is None
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


@pytest.fixture
def arm_b(monkeypatch, request):
    from ros_esc.supervisor_node import stationary_centroid as module
    rclpy.init()
    now, steady = [ORIGIN_NS], [5_000_000_000]
    monkeypatch.setattr(module.time, 'monotonic_ns', lambda: steady[0])
    node = SupervisorNode(parameter_overrides=[
        Parameter('algorithm_profile', value='robust_gaussian_v1'),
        Parameter('continuous_search_mode', value='stationary_v1'),
        Parameter('convergence_metric_mode', value='centroid_windows_v2'),
        Parameter('use_sim_time', value=True),
        Parameter('pose_topic', value='/selected/odom'),
        Parameter('operating_bounds_enabled', value=False),
        Parameter('extremum_classification_mode', value='counted_candidates'),
        Parameter('known_source_count', value=2),
        Parameter('max_fill_clusters', value=1),
        Parameter('candidate_cost_rotation_period_sec', value=.25),
        Parameter('candidate_cost_required_rotations', value=2),
        Parameter('candidate_informed_fill_enabled', value=True),
        Parameter('recenter_after_escape', value=False),
        Parameter('recording_ready_required', value=bool(getattr(request, 'param', False))),
    ])
    node.get_clock = lambda: SimpleNamespace(now=lambda: Time(nanoseconds=now[0]))
    # Initialize the real state machine in the simulated run's nonzero epoch;
    # no transition input or verification output is substituted below.
    node.machine = SupervisorStateMachine(now_sec=ORIGIN_NS*1e-9, config=node.machine.config)
    node.started_sec = ORIGIN_NS*1e-9
    node.state_publisher, node.event_publisher, node.fill_request_publisher = Recorder(), Recorder(), Recorder()
    node.stationary_centroid.request_publisher = Recorder()
    node.stationary_centroid.timekeeper(Timekeeper(mode='sim time', start_time=ORIGIN_NS*1e-9))
    try:
        yield node, now, steady
    finally:
        node.destroy_node()
        rclpy.shutdown()


def heartbeat(node, *, cost=-1.):
    pose = _pose(1., 2.)
    pose.header.frame_id = 'odom'
    set_time(pose.header.stamp, node.get_clock().now().nanoseconds)
    node.pose_callback(pose)
    node.source_callback(_source(raw_cost=cost))


def enter_confirmation(arm_b, *, lead_ns=0, message=None):
    node, now, steady = arm_b
    now[0] = ORIGIN_NS+19_000_000_000-lead_ns
    heartbeat(node)
    msg = confirmation() if message is None else message
    msg.run_id = node.run_id
    node.stationary_centroid.confirmation(msg)
    node.timer_callback()
    return msg


def finish_verification(arm_b):
    node, now, steady = arm_b
    for _ in range(14):
        if node.machine.state == State.DESIGN_OR_MERGE_FILL:
            break
        now[0] += 50_000_000
        steady[0] += 50_000_000
        heartbeat(node)
        node.timer_callback()
    assert node.machine.state == State.DESIGN_OR_MERGE_FILL


def test_typed_confirmation_uses_real_stopped_verification_then_typed_create(arm_b):
    node, now, steady = arm_b
    original = deepcopy(enter_confirmation(arm_b))
    assert node.machine.state == State.VERIFY_EXTREMUM
    assert node.machine.config.moving_verification_enabled is False
    assert not node.stationary_centroid.request_publisher.messages
    assert node.current_supervisor_command.linear.x == node.current_supervisor_command.angular.z == 0.
    assert not CustomController._state_allows_motion(
        SimpleNamespace(v2_enabled=False), node.state_publisher.messages[-1])
    finish_verification(arm_b)
    requests = node.stationary_centroid.request_publisher.messages
    assert len(requests) == 1 and not node.fill_request_publisher.messages
    request = requests[0]
    assert request.confirmation == original
    assert request.operation == request.CREATE and request.candidate_evidence_valid
    assert request.candidate_rotation_count == 2
    assert request.candidate_cost_estimate == request.candidate_cost_lower == -1.
    assert request.source_timestamp == (time_to_ns(request.stamp)-ORIGIN_NS)*1e-9
    assert node.machine.fill_request_timestamp == request.source_timestamp
    assert time_to_ns(request.confirmation_received_at) == ORIGIN_NS+19_000_000_000
    assert time_to_ns(request.confirmation_accepted_at) == ORIGIN_NS+19_000_000_000
    assert time_to_ns(request.expires_at) == round(
        (node.machine.state_entered_sec+node.machine.config.fill_design_timeout_sec)*1e9)
    assert node.current_supervisor_command.linear.x == node.current_supervisor_command.angular.z == 0.
    assert not CustomController._state_allows_motion(
        SimpleNamespace(v2_enabled=False), node.state_publisher.messages[-1])
    from ros_esc.stationary_fill_protocol import stationary_request_errors
    assert stationary_request_errors(request, expected_run_id=node.run_id,
        expected_frame_id='odom', expected_pose_topic='/selected/odom', origin_ns=ORIGIN_NS) == []


def test_arm_b_ignores_legacy_confirmation_event_and_pde_status(arm_b):
    node, now, steady = arm_b
    now[0] += 19_000_000_000
    heartbeat(node)
    node.convergence_callback(_convergence(1., 2.))
    node.event_callback(_confirmed_convergence(1., 2.))
    node.timer_callback()
    assert node.machine.state == State.SEARCH
    assert node.stationary_centroid.accepted is None
    assert not node.stationary_centroid.request_publisher.messages


def test_100ms_leading_confirmation_waits_then_retains_original_receipt(arm_b):
    node, now, steady = arm_b
    original = deepcopy(enter_confirmation(arm_b, lead_ns=100_000_000))
    received = now[0]
    assert node.machine.state == State.SEARCH and node.stationary_centroid.accepted is None
    now[0] += 100_000_000
    steady[0] += 100_000_000
    heartbeat(node)
    node.timer_callback()
    assert node.machine.state == State.VERIFY_EXTREMUM
    finish_verification(arm_b)
    request = node.stationary_centroid.request_publisher.messages[0]
    assert request.confirmation == original
    assert time_to_ns(request.confirmation_received_at) == received
    assert time_to_ns(request.confirmation_accepted_at) == received+100_000_000


def test_paused_clock_duplicate_cannot_refresh_pending_confirmation_lease(arm_b):
    node, now, steady = arm_b
    msg = enter_confirmation(arm_b, lead_ns=100_000_000)
    steady[0] += 400_000_000
    node.stationary_centroid.confirmation(deepcopy(msg))
    steady[0] += 100_000_001
    node.stationary_centroid.poll()
    now[0] += 100_000_000
    heartbeat(node)
    node.stationary_centroid.confirmation(deepcopy(msg))
    node.timer_callback()
    assert node.machine.state == State.SEARCH
    assert node.stationary_centroid.accepted is None


@pytest.mark.parametrize('change', [
    'wrong_run', 'wrong_frame', 'wrong_topic', 'old_epoch_start',
    'not_confirmed', 'score_mismatch', 'window_mismatch',
    'wrong_selected_epsilon', 'wrong_selected_radius',
])
def test_invalid_confirmation_never_enters_verification(arm_b, change):
    node, now, steady = arm_b
    now[0] += 19_000_000_000
    heartbeat(node)
    msg = confirmation(); msg.run_id = node.run_id
    if change == 'wrong_run': msg.run_id = 'unrelated-run'
    elif change == 'wrong_frame': msg.frame_id = 'map'
    elif change == 'wrong_topic': msg.source_pose_topic = '/wrong/odom'
    elif change == 'old_epoch_start': set_time(msg.epoch_started_at, ORIGIN_NS-1_000_000_000)
    elif change == 'not_confirmed': msg.confirmed = False
    elif change == 'score_mismatch': msg.score_m = .01
    elif change == 'window_mismatch': msg.window_end[-1].sec += 1
    elif change == 'wrong_selected_epsilon': msg.epsilon_m = .07
    elif change == 'wrong_selected_radius': msg.maximum_radius_m = .6
    node.stationary_centroid.confirmation(msg)
    node.timer_callback()
    assert node.machine.state == State.SEARCH
    assert node.stationary_centroid.accepted is None


@pytest.mark.parametrize('origin', [-1., 1001.])
def test_malformed_or_changed_timekeeper_cannot_authorize_confirmation(arm_b, origin):
    node, now, steady = arm_b
    node.stationary_centroid.timekeeper(Timekeeper(mode='sim time', start_time=origin))
    enter_confirmation(arm_b)
    assert node.machine.state != State.VERIFY_EXTREMUM
    assert node.stationary_centroid.accepted is None


def test_accepted_confirmation_cannot_be_replaced_during_verification(arm_b):
    node, now, steady = arm_b
    original = deepcopy(enter_confirmation(arm_b))
    duplicate = deepcopy(original)
    duplicate.center_x_m = 9.
    duplicate.centroid_x_m = [9.]*6
    node.stationary_centroid.confirmation(duplicate)
    assert node.stationary_centroid.candidate_center() == pytest.approx((1., 2.))
    finish_verification(arm_b)
    assert node.stationary_centroid.request_publisher.messages[0].confirmation == original


def test_explicit_stop_still_beats_valid_typed_confirmation(arm_b):
    node, now, steady = arm_b
    node.stop_callback(Bool(data=True))
    enter_confirmation(arm_b)
    assert node.machine.state == State.FAILSAFE
    assert not node.stationary_centroid.request_publisher.messages
    assert node.current_supervisor_command.linear.x == node.current_supervisor_command.angular.z == 0.


def test_same_clock_redesign_waits_without_changing_original_deadline_or_candidate(arm_b):
    node, now, steady = arm_b
    enter_confirmation(arm_b); finish_verification(arm_b)
    adapter = node.stationary_centroid
    first = deepcopy(adapter.request_publisher.messages[0])
    # Seed the inherited accepted-fill escape state; exercise its real stall
    # transition into the same stationary DESIGN hook at a held clock value.
    node.machine.state = State.ESCAPE_REPULSE
    node.machine.state_entered_sec = now[0]*1e-9
    node.machine.escape_started_sec = now[0]*1e-9
    node.machine.active_escape_fill_id = 7
    node.machine.active_fill_count = 1
    node.active_fill_records[3] = dict(fill_id=7, revision=2, center=(1., 2.),
                                      support_radius=.5, exit_radius=.5)
    transition = node.machine.step(now[0]*1e-9, TransitionInputs(stalled=True))
    assert transition.current == State.DESIGN_OR_MERGE_FILL
    node._handle_transition(transition, now[0]*1e-9)
    assert len(adapter.request_publisher.messages) == 1
    original_deadline = round((node.machine.state_entered_sec+node.machine.config.fill_design_timeout_sec)*1e9)
    for _ in range(3): adapter.poll()
    assert len(adapter.request_publisher.messages) == 1
    now[0] += 100_000_000; steady[0] += 100_000_000
    adapter.poll()
    assert len(adapter.request_publisher.messages) == 2
    redesign = adapter.request_publisher.messages[-1]
    assert redesign.operation == redesign.TARGETED_REDESIGN
    assert (redesign.target_fill_id, redesign.target_cluster_id, redesign.target_revision) == (7, 3, 2)
    assert not redesign.candidate_evidence_valid
    assert redesign.confirmation == first.confirmation
    assert redesign.confirmation_received_at == first.confirmation_received_at
    assert redesign.confirmation_accepted_at == first.confirmation_accepted_at
    assert time_to_ns(redesign.expires_at) == original_deadline
    assert redesign.source_timestamp > first.source_timestamp+1e-9
    assert node.machine.fill_request_timestamp == redesign.source_timestamp
    assert node.machine.step(now[0]*1e-9, TransitionInputs(
        fill_result='success', fill_source_timestamp=first.source_timestamp,
        fill_id=7, active_fill_count=1)) is None
    assert node.machine.state == State.DESIGN_OR_MERGE_FILL


def test_prior_confirmation_cannot_rearm_after_search_reentry(arm_b):
    node, now, steady = arm_b
    original = deepcopy(enter_confirmation(arm_b))
    now[0] += 100_000_000; steady[0] += 100_000_000
    transition = node.machine._transition(State.SEARCH, now[0]*1e-9, 'synthetic verification rejection')
    node._handle_transition(transition, now[0]*1e-9)
    heartbeat(node)
    node.stationary_centroid.confirmation(original)
    node.timer_callback()
    assert node.machine.state == State.SEARCH and node.stationary_centroid.accepted is None
    assert not node.stationary_centroid.request_publisher.messages


@pytest.mark.parametrize('arm_b', [True], indirect=True)
def test_recording_authority_is_required_before_typed_confirmation(arm_b):
    node, now, steady = arm_b
    refused = enter_confirmation(arm_b)
    assert node.machine.state == State.SEARCH
    node.stationary_centroid.readiness(Bool(data=True))
    node.stationary_centroid.confirmation(deepcopy(refused)); node.timer_callback()
    assert node.machine.state == State.SEARCH
    assert not node.stationary_centroid.request_publisher.messages


@pytest.mark.parametrize('arm_b', [True], indirect=True)
def test_recording_revocation_prevents_design_after_valid_confirmation(arm_b):
    node, now, steady = arm_b
    node.stationary_centroid.readiness(Bool(data=True))
    enter_confirmation(arm_b)
    assert node.machine.state == State.VERIFY_EXTREMUM
    node.stationary_centroid.readiness(Bool(data=False))
    assert node.machine.state == State.FAILSAFE
    assert not node.stationary_centroid.request_publisher.messages


@pytest.mark.parametrize('arm_b', [True], indirect=True)
def test_expired_recording_lease_fences_accepted_historical_candidate(arm_b):
    node, now, steady = arm_b
    node.stationary_centroid.readiness(Bool(data=True))
    enter_confirmation(arm_b)
    assert node.machine.state == State.VERIFY_EXTREMUM
    steady[0] += node.stationary_centroid.ready_stale_ns+1
    node.stationary_centroid.poll()
    assert node.machine.state == State.FAILSAFE
    assert not node.stationary_centroid.request_publisher.messages


@pytest.mark.parametrize('fault', ['missing_target', 'capacity'])
def test_dispatch_failsafe_cannot_be_followed_by_obsolete_design_transition(arm_b, monkeypatch, fault):
    from ros_esc.supervisor_node import stationary_centroid as module
    node, now, steady = arm_b
    enter_confirmation(arm_b); finish_verification(arm_b)
    now[0] += 100_000_000; steady[0] += 100_000_000
    node.machine.state = State.ESCAPE_REPULSE
    node.machine.design_returns_to_assist = fault == 'missing_target'
    node.machine.active_escape_fill_id = 99
    if fault == 'capacity': monkeypatch.setattr(module, 'MAX_COMMANDS', 1)
    transition = node.machine._transition(
        State.DESIGN_OR_MERGE_FILL, now[0]*1e-9, 'synthetic adapter rejection boundary')
    node._handle_transition(transition, now[0]*1e-9)
    assert node.machine.state == State.FAILSAFE
    transitions = [msg for msg in node.event_publisher.messages
                   if msg.event_type == AlgorithmEvent.EVENT_STATE_TRANSITION]
    assert transitions and '->FAILSAFE:' in transitions[-1].detail
    assert len(node.stationary_centroid.request_publisher.messages) == 1
    assert node.current_supervisor_command.linear.x == node.current_supervisor_command.angular.z == 0.


def test_b_state_publication_uses_one_clock_snapshot_for_stamp_and_elapsed(arm_b):
    node, now, steady = arm_b
    caller_time = now[0]*1e-9
    now[0] += 100_000_000  # Clock advanced inside the caller's callback.
    node._publish_state_and_command(caller_time)
    state = node.state_publisher.messages[-1]
    reconstructed_entry = time_to_ns(state.stamp)-round(state.state_elapsed_sec*1e9)
    assert reconstructed_entry == round(node.machine.state_entered_sec*1e9)
