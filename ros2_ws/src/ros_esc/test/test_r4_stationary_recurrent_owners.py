"""Recurrent evidence through actual stationary verification and robust fit owners."""
from copy import deepcopy
from functools import lru_cache
from types import SimpleNamespace

import pytest
import rclpy
from builtin_interfaces.msg import Time as WireTime
from rclpy.parameter import Parameter
from rclpy.serialization import deserialize_message, serialize_message
from rclpy.time import Time
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import AlgorithmState, RecurrentConvergenceDiagnostics, StationaryRecurrentFillRequest, Timekeeper
from ros_esc.gaussian_fill_node import gaussian_fill_script as gaussian
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.state_machine import State, SupervisorStateMachine
from ros_esc.stationary_fill_protocol import stationary_request_errors, stationary_request_sha256
from ros_esc.v2_stream import set_time, time_to_ns
from test_q5_stationary_fill_protocol import ORIGIN_NS, RUN, POSE, confirmation as centroid, request as centroid_request
from test_q5_stationary_centroid_adapter import heartbeat, finish_verification
from test_q5_stationary_gaussian_contract import seed_support, live_state, active_fill
from test_supervisor_integration import Recorder
from test_r3_recurrent_startup import RECORDED, OWNERS

MODE = 'recurrent_geometry_v3'
NS = 1_000_000_000


@lru_cache(maxsize=1)
def _confirmation_wire():
    # Use the actual fixed model, then transport its first circle confirmation.
    from test_recurrent_geometry import run_trace, diagnostic
    _, rows = run_trace('circle', duration=42.)
    row = next(row for row in rows if row.confirmed_event)
    assert row.end_ns == 42*NS
    values = vars(diagnostic(row))
    for name in ('stamp', 'receipt_stamp', 'source_stamp', 'epoch_started_at',
                 'history_start', 'history_end', 'persistence_start'):
        values[name] = set_time(WireTime(), time_to_ns(values[name])+ORIGIN_NS)
    values.update(run_id=RUN, source_pose_topic=POSE)
    return serialize_message(RecurrentConvergenceDiagnostics(**values))


def confirmation():
    return deserialize_message(_confirmation_wire(), RecurrentConvergenceDiagnostics)


def request():
    original = centroid_request()
    msg = StationaryRecurrentFillRequest()
    for name in msg.get_fields_and_field_types():
        if name != 'confirmation':
            setattr(msg, name, deepcopy(getattr(original, name)))
    msg.confirmation = confirmation()
    for name in ('stamp', 'expires_at', 'confirmation_received_at', 'confirmation_accepted_at'):
        field = getattr(msg, name)
        set_time(field, time_to_ns(field)+23*NS)
    msg.source_timestamp = 48.
    msg.request_sha256 = stationary_request_sha256(msg)
    return msg


@pytest.fixture(autouse=True)
def isolated_domain(monkeypatch):
    monkeypatch.setenv('ROS_DOMAIN_ID', '204')
    monkeypatch.setenv('ROS_LOCALHOST_ONLY', '1')


@pytest.mark.parametrize('name', list(OWNERS))
def test_recorded_selected_constructor_routes_stationary_recurrent(name):
    rclpy.init(args=RECORDED[name]+['-p', 'continuous_search_mode:=stationary_v1',
        '-p', 'v2_verification_motion_mode:=rolling_neighborhood_v1'])
    node = None
    try:
        node = OWNERS[name]()
        adapter = node.stationary_fill if name == 'gaussian_fill_node' else node.stationary_centroid
        assert adapter.request_type is StationaryRecurrentFillRequest
        assert adapter.contract['request_topic'] == '/gesc_gaussian/v2/stationary_recurrent_fill_requests'
        if name == 'gaussian_fill_node':
            assert node.v2_fill is None and adapter.metric_parameters is None
        else:
            assert node.moving_v2 is None and adapter.configuration is None
            assert adapter.diagnostics_type is RecurrentConvergenceDiagnostics
            assert any(sub.msg_type is RecurrentConvergenceDiagnostics and sub.topic_name ==
                '/gesc_gaussian/v2/recurrent_convergence_diagnostics' for sub in node.subscriptions)
    finally:
        if node is not None: node.destroy_node()
        rclpy.try_shutdown()


def test_centered_motion_still_requires_rolling_verification():
    rclpy.init(args=RECORDED['supervisor_node']+['-p', 'continuous_search_mode:=stationary_v1'])
    try:
        with pytest.raises(ValueError, match='centered tracking requires selected rolling simulation'):
            SupervisorNode()
    finally: rclpy.try_shutdown()


@pytest.fixture
def supervisor(monkeypatch):
    from ros_esc.supervisor_node import stationary_centroid as module
    rclpy.init()
    now, steady = [ORIGIN_NS], [5*NS]
    monkeypatch.setattr(module.time, 'monotonic_ns', lambda: steady[0])
    parameters = dict(algorithm_profile='robust_gaussian_v1', continuous_search_mode='stationary_v1',
        convergence_metric_mode=MODE, use_sim_time=True, pose_topic=POSE,
        operating_bounds_enabled=False, extremum_classification_mode='counted_candidates',
        known_source_count=2, max_fill_clusters=1, candidate_cost_rotation_period_sec=.25,
        candidate_cost_required_rotations=2, candidate_informed_fill_enabled=True,
        recenter_after_escape=False, recording_ready_required=False)
    node = SupervisorNode(parameter_overrides=[Parameter(k, value=v) for k,v in parameters.items()])
    node.get_clock = lambda: SimpleNamespace(now=lambda: Time(nanoseconds=now[0]))
    node.machine = SupervisorStateMachine(now_sec=ORIGIN_NS*1e-9, config=node.machine.config)
    node.started_sec = ORIGIN_NS*1e-9
    node.state_publisher, node.event_publisher, node.fill_request_publisher = Recorder(), Recorder(), Recorder()
    node.stationary_centroid.request_publisher = Recorder()
    node.stationary_centroid.timekeeper(Timekeeper(mode='sim time', start_time=ORIGIN_NS*1e-9))
    try: yield node, now, steady
    finally:
        node.destroy_node(); rclpy.try_shutdown()


def enter(supervisor, lead_ns=0):
    node, now, _ = supervisor
    now[0] = ORIGIN_NS+42*NS-lead_ns
    heartbeat(node)
    msg = confirmation(); msg.run_id = node.run_id
    node.stationary_centroid.confirmation(msg); node.timer_callback()
    return msg


def test_actual_stopped_verification_preserves_typed_history_and_original_admission(supervisor):
    node, now, steady = supervisor
    msg = enter(supervisor, 100_000_000)
    received = now[0]
    assert node.machine.state == State.SEARCH
    now[0] += 100_000_000; steady[0] += 100_000_000
    heartbeat(node); node.timer_callback()
    assert node.machine.state == State.VERIFY_EXTREMUM
    assert not node.machine.config.moving_verification_enabled
    assert node.current_supervisor_command.linear.x == node.current_supervisor_command.angular.z == 0.
    finish_verification(supervisor)
    requests = node.stationary_centroid.request_publisher.messages
    assert len(requests) == 1 and not node.fill_request_publisher.messages
    result = requests[0]
    assert type(result) is StationaryRecurrentFillRequest
    assert serialize_message(result.confirmation) == serialize_message(msg)
    assert time_to_ns(result.confirmation_received_at) == received
    assert time_to_ns(result.confirmation_accepted_at) == received+100_000_000
    assert result.candidate_evidence_valid and result.candidate_rotation_count == 2
    assert result.candidate_cost_estimate == result.candidate_cost_lower == -1.
    assert stationary_request_errors(result, expected_run_id=node.run_id,
        expected_pose_topic=POSE, expected_frame_id='odom', origin_ns=ORIGIN_NS,
        expected_metric_mode=MODE) == []
    assert node.current_supervisor_command.linear.x == node.current_supervisor_command.angular.z == 0.


def test_confirmation_duplicate_cannot_refresh_original_steady_lease(supervisor):
    node, now, steady = supervisor
    msg = enter(supervisor, 100_000_000)
    pending = node.stationary_centroid.pending_confirmation
    steady[0] += 400_000_000
    node.stationary_centroid.confirmation(deepcopy(msg))
    assert node.stationary_centroid.pending_confirmation is pending
    steady[0] += 100_000_001
    node.stationary_centroid.poll()
    now[0] += 100_000_000; heartbeat(node)
    node.stationary_centroid.confirmation(deepcopy(msg)); node.timer_callback()
    assert node.machine.state == State.SEARCH and node.stationary_centroid.accepted is None


@pytest.mark.parametrize('fault', ['centroid_type', 'persistence_before_origin', 'stop'])
def test_selected_confirmation_admission_guards(supervisor, fault):
    node, now, _ = supervisor
    now[0] = ORIGIN_NS+42*NS; heartbeat(node)
    msg = confirmation(); msg.run_id = node.run_id
    if fault == 'centroid_type': msg = centroid()
    elif fault == 'persistence_before_origin':
        # Move the observed run origin after persistence began, but before fit support.
        node.stationary_centroid.origin_ns = ORIGIN_NS+NS
    else: node.stop_callback(Bool(data=True))
    node.stationary_centroid.confirmation(msg); node.timer_callback()
    assert node.machine.state != State.VERIFY_EXTREMUM
    assert node.stationary_centroid.accepted is None
    assert not node.stationary_centroid.request_publisher.messages


@pytest.fixture
def fill_node():
    rclpy.init(args=['--ros-args', '-p', 'algorithm_profile:=robust_gaussian_v1',
        '-p', 'convergence_metric_mode:='+MODE, '-p', 'continuous_search_mode:=stationary_v1',
        '-p', 'use_sim_time:=true', '-p', 'pose_topic:='+POSE])
    node = gaussian.GaussianFill()
    now, steady = [ORIGIN_NS+48*NS], [5*NS]
    node.get_clock = lambda: SimpleNamespace(now=lambda: Time(nanoseconds=now[0]))
    node.stationary_fill.steady = lambda: steady[0]
    node.stationary_fill.set_timekeeper(Timekeeper(mode='sim time', start_time=ORIGIN_NS*1e-9))
    try: yield node, now, steady
    finally:
        node.destroy_node(); rclpy.try_shutdown()


def design(node, now_ns):
    return live_state(node, now_ns, began_ns=ORIGIN_NS+48*NS)


def test_actual_fit_uses_original_receipt_frozen_samples_and_duplicate_replays(fill_node, monkeypatch):
    node, now, steady = fill_node
    now[0] -= 100_000_000; seed_support(node, now[0])
    original_poses, original_costs = tuple(node.pose_snapshots), tuple(node.cost_snapshots)
    msg = request(); node.stationary_fill.request_cb(msg)
    pending = node.stationary_fill.pending
    assert pending is not None and pending.receipt_ns == now[0]
    assert pending.steady_ns == steady[0]
    assert pending.pose_snapshots == original_poses and pending.cost_snapshots == original_costs
    node.pose_snapshots.clear(); node.cost_snapshots.clear()
    msg.confirmation.center_x_m = 999.
    now[0] += 100_000_000; steady[0] += 100_000_000
    design(node, now[0]); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1, node.stationary_fill.last_reason
    assert active_fill(node).source_timestamp == 48.
    assert active_fill(node).sample_count > 0
    def forbidden(*args, **kwargs): raise AssertionError('duplicate refit')
    monkeypatch.setattr(gaussian, 'estimate_basin', forbidden)
    now[0] += 10*NS
    node.stationary_fill.request_cb(request()); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1 and node.stationary_fill.requests[1] is pending


@pytest.mark.parametrize('fault', ['deadline', 'stop', 'origin_change', 'run_change'])
def test_authority_revocation_during_actual_fit_blocks_commit(fill_node, monkeypatch, fault):
    node, now, _ = fill_node
    seed_support(node, now[0]); design(node, now[0])
    estimate = gaussian.estimate_basin
    calls = []
    def revoke(*args, **kwargs):
        result = estimate(*args, **kwargs); calls.append(True)
        if fault == 'deadline': now[0] = ORIGIN_NS+53*NS
        elif fault == 'origin_change':
            node.stationary_fill.set_timekeeper(Timekeeper(mode='sim time', start_time=1001.))
        else:
            now[0] += 1
            live_state(node, now[0], began_ns=ORIGIN_NS+48*NS,
                state=AlgorithmState.STATE_FAILSAFE if fault == 'stop' else AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
                run='other' if fault == 'run_change' else RUN)
        return result
    monkeypatch.setattr(gaussian, 'estimate_basin', revoke)
    node.stationary_fill.request_cb(request()); node.stationary_fill.poll()
    assert calls and node.fill_registry.generation == 0


def test_wrong_envelope_cannot_reach_fit(fill_node, monkeypatch):
    node, now, _ = fill_node
    seed_support(node, now[0]); design(node, now[0])
    def forbidden(*args, **kwargs): raise AssertionError('wrong envelope fit')
    monkeypatch.setattr(gaussian, 'estimate_basin', forbidden)
    node.stationary_fill.request_cb(centroid_request()); node.stationary_fill.poll()
    assert not node.stationary_fill.requests and node.fill_registry.generation == 0
