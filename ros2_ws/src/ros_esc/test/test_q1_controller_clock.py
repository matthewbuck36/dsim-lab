"""Controller admission regressions for the recorded held simulation clock."""

from copy import deepcopy

import pytest
from rclpy.time import Time

from ros_esc.controller_node import controller_node_script as controller
from ros_esc.controller_node.clock_admission import ClockAdmission, FRESHNESS_NS, MAX_PENDING
from ros_esc.v2_stream import set_time
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray, Timekeeper
from test_v2_controller_motion import node_factory, prepare, pose, state, command, GESC, SUPERVISOR


def message(kind, stamp):
    if kind == 'pose':
        return pose(stamp)
    if kind == 'state':
        return state(AlgorithmState.STATE_SEARCH, stamp=stamp)
    return StampedFloat64MultiArray(timestamp=stamp, data=[.08, .04])


def receive(node, kind, msg):
    {'pose': node.state_callback, 'state': node.supervisor_state_callback,
     'filter': node.input_value_callback}[kind](msg)


def source(node, kind):
    return {'pose': node.v2_pose_source_ns, 'state': node.v2_last_state_source_ns,
            'filter': node.v2_input_source_ns}[kind]


def receipt(node, kind):
    return {'pose': node.pose_receipt_sec, 'state': node.supervisor_state_receipt_sec,
            'filter': node.input_receipt_sec}[kind]


@pytest.mark.parametrize('kind', ['pose', 'filter', 'state'])
def test_near_future_keeps_covered_active_until_clock_admission(node_factory, kind):
    node = node_factory()
    prepare(node, state(AlgorithmState.STATE_SEARCH))
    node.algorithm_event_publisher.messages.clear()
    incoming = message(kind, 10.021)
    receive(node, kind, incoming)
    assert source(node, kind) == 10_000_000_000
    original = node.v2_admission.pending[kind][0]
    node.watchdog_callback()
    assert not node.algorithm_event_publisher.messages
    assert node._motion_authorized(node.latest_algorithm_state)
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node._v2_admission_tick()
    assert source(node, kind) == 10_021_000_000
    assert receipt(node, kind) == 10.
    assert node.v2_active_steady[kind] == original.steady_ns
    assert not node.v2_admission.pending[kind]
    assert not node.algorithm_event_publisher.messages


@pytest.mark.parametrize('kind', ['pose', 'filter', 'state'])
def test_exact_duplicate_never_refreshes_ros_or_steady_receipt(node_factory, kind):
    node = node_factory()
    prepare(node, state(AlgorithmState.STATE_SEARCH))
    first = node.v2_active_steady[kind]
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_200_000_000))
    receive(node, kind, message(kind, 10.))
    assert receipt(node, kind) == 10.
    assert node.v2_active_steady[kind] == first
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_501_000_000))
    node.watchdog_callback()
    assert node.twist_publisher.messages[-1].linear.x == 0.


@pytest.mark.parametrize('kind', ['pose', 'filter', 'state'])
@pytest.mark.parametrize('fault', ['regression', 'far_future', 'stale', 'invalid'])
def test_invalid_data_revokes_active_and_pending_without_grace(node_factory, kind, fault):
    node = node_factory()
    prepare(node, state(AlgorithmState.STATE_SEARCH))
    receive(node, kind, message(kind, 10.1))
    value = {'regression': 10.01, 'far_future': 10.500001, 'stale': 9.49, 'invalid': 10.2}[fault]
    bad = message(kind, value)
    if fault == 'invalid':
        if kind == 'pose': bad.pose.pose.position.x = float('nan')
        elif kind == 'filter': bad.data = [float('nan'), 0.]
        else: bad.run_id = 'wrong-run'
    receive(node, kind, bad)
    assert kind in node.v2_admission_faults
    assert not node.v2_admission.pending[kind]
    assert node.twist_publisher.messages[-1].linear.x == node.twist_publisher.messages[-1].angular.z == 0.
    assert node.algorithm_event_publisher.messages


def test_pose_conflict_revokes_and_retransmission_cannot_restore(node_factory):
    node = node_factory()
    prepare(node)
    changed = pose()
    changed.pose.pose.position.x = .2
    node.state_callback(changed)
    assert 'conflicting duplicate' in node.v2_admission_faults['pose']
    node.state_callback(pose())
    assert node.v2_pose_source_ns is None
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node.state_callback(pose(10.1))
    assert node.v2_pose_source_ns == 10_100_000_000
    assert 'pose' not in node.v2_admission_faults


@pytest.mark.parametrize('kind', ['filter', 'state'])
def test_same_publication_tick_revisions_keep_order(node_factory, kind):
    node = node_factory()
    prepare(node)
    first, second = message(kind, 10.1), message(kind, 10.1)
    if kind == 'state':
        second.state = AlgorithmState.STATE_VERIFY_EXTREMUM
    else:
        first.data, second.data = [.05, .01], [.06, .02]
    receive(node, kind, first)
    receive(node, kind, second)
    assert len(node.v2_admission.pending[kind]) == 2
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node._v2_admission_tick()
    if kind == 'state': assert node.latest_algorithm_state == second
    else: assert list(node.input_value) == list(second.data)
    assert not node.v2_admission_faults


@pytest.mark.parametrize('stop', [AlgorithmState.STATE_GOAL_HOLD, AlgorithmState.STATE_FAILSAFE])
def test_future_stop_fences_older_queued_search_and_filter_commands(node_factory, stop):
    node = node_factory()
    prepare(node, state(AlgorithmState.STATE_SEARCH))
    node.supervisor_state_callback(state(AlgorithmState.STATE_SEARCH, stamp=10.05))
    node.input_value_callback(message('filter', 10.05))
    node.supervisor_state_callback(state(stop, stamp=10.1))
    assert node.v2_state_fenced
    assert node.twist_publisher.messages[-1].linear.x == 0.
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_050_000_000))
    node._v2_admission_tick()
    assert node.latest_algorithm_state.state == AlgorithmState.STATE_SEARCH
    assert node.v2_state_fenced
    assert list(node.controller_publisher.messages[-1].data) == [0.]*6
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node._v2_admission_tick()
    assert node.latest_algorithm_state.state == stop
    assert not node._motion_authorized(node.latest_algorithm_state)


@pytest.mark.parametrize('kind', ['pose', 'filter', 'state'])
@pytest.mark.parametrize('clock', ['ros', 'steady'])
def test_pending_original_receipt_expiry_fails_even_if_source_is_fresh(node_factory, monkeypatch, kind, clock):
    node = node_factory()
    prepare(node)
    receive(node, kind, message(kind, 10.2))
    item = node.v2_admission.pending[kind][0]
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_501_000_000 if clock == 'ros' else 10_200_000_000))
    if clock == 'steady':
        monkeypatch.setattr(controller.time, 'monotonic_ns', lambda: item.steady_ns+500_000_001)
    node._v2_admission_tick()
    assert 'original pending receipt' in node.v2_admission_faults[kind]
    assert node.twist_publisher.messages[-1].linear.x == 0.


def test_held_clock_active_receipts_expire_without_a_ros_timer_tick(node_factory, monkeypatch):
    node = node_factory()
    prepare(node)
    after = max(node.v2_active_steady.values())+500_000_001
    monkeypatch.setattr(controller.time, 'monotonic_ns', lambda: after)
    node._v2_admission_tick()
    assert 'steady receipt' in node._robust_fault_reason()
    assert node.twist_publisher.messages[-1].linear.x == 0.


@pytest.mark.parametrize('fault', ['rollback', 'origin'])
def test_clock_context_loss_clears_pending_and_active(node_factory, fault):
    node = node_factory()
    prepare(node)
    for kind in ('state', 'pose', 'filter'):
        receive(node, kind, message(kind, 10.1))
    if fault == 'rollback':
        node.get_clock().set_ros_time_override(Time(seconds=9))
        node._v2_admission_tick()
    else:
        node.timekeeping_callback(Timekeeper(mode='sim time', start_time=1.))
    assert all(not q for q in node.v2_admission.pending.values())
    assert not node.v2_active_steady
    assert node.state_value is node.input_value is node.latest_algorithm_state is None
    assert node.twist_publisher.messages[-1].linear.x == 0.


@pytest.mark.parametrize('kind', ['state', 'pose', 'filter'])
def test_capacity_is_bounded_and_never_silently_drops_pending(kind):
    admission = ClockAdmission()
    for index in range(MAX_PENDING):
        admission.receive(kind, index+1, 0, 0, index, limit_ns=FRESHNESS_NS)
    with pytest.raises(ValueError, match='capacity'):
        admission.receive(kind, MAX_PENDING+1, 0, 0, 'overflow', limit_ns=FRESHNESS_NS)
    assert len(admission.pending[kind]) == MAX_PENDING


@pytest.mark.parametrize('kind', ['state', 'pose', 'filter'])
def test_node_capacity_fault_clears_active_and_pending(node_factory, kind):
    node = node_factory()
    prepare(node)
    for index in range(MAX_PENDING):
        node.v2_admission.receive(kind, 10_000_000_001+index, 10_000_000_000,
                                  controller.time.monotonic_ns(), index, limit_ns=FRESHNESS_NS)
    receive(node, kind, message(kind, 10.1))
    assert 'capacity' in node.v2_admission_faults[kind]
    assert not node.v2_admission.pending[kind]
    assert node.twist_publisher.messages[-1].linear.x == 0.


@pytest.mark.parametrize('kind', ['state', 'pose'])
def test_first_origin_cannot_admit_earlier_unbound_pending_sample(node_factory, kind):
    node = node_factory()
    receive(node, kind, message(kind, 10.1))
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=10.2))
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_200_000_000))
    node._v2_admission_tick()
    assert kind in node.v2_admission_faults
    assert not node.v2_admission.pending[kind]


def test_pending_message_copy_does_not_alias_caller(node_factory):
    node = node_factory()
    prepare(node)
    item = pose(10.1)
    node.state_callback(item)
    item.pose.pose.position.x = float('nan')
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node._v2_admission_tick()
    assert node.state_value[0] == 0.


def test_real_state_unavailable_nan_fields_do_not_refresh_retransmission(node_factory):
    node = node_factory()
    original = state()
    original.escape_center_x = original.escape_center_y = float('nan')
    original.recenter_distance = original.radial_progress = float('nan')
    prepare(node, original)
    first = node.v2_active_steady['state']
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node.supervisor_state_callback(deepcopy(original))
    assert node.supervisor_state_receipt_sec == 10.
    assert node.v2_active_steady['state'] == first


def test_clock_rollback_during_admission_cannot_restore_detached_batch(node_factory, monkeypatch):
    node = node_factory()
    prepare(node)
    node.state_callback(pose(10.1))
    original = node.v2_admission.covered
    def rollback(*args, **kwargs):
        values = original(*args, **kwargs)
        if args[0] == 'pose': node.get_clock().set_ros_time_override(Time(seconds=9))
        return values
    monkeypatch.setattr(node.v2_admission, 'covered', rollback)
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node._v2_admission_tick()
    assert node.state_value is None and not node.v2_active_steady


def test_all_three_future_inputs_use_only_covered_values(node_factory):
    node = node_factory()
    prepare(node, state(AlgorithmState.STATE_SEARCH))
    for kind in ('state', 'pose', 'filter'):
        item = message(kind, 10.1)
        if kind == 'filter': item.data = [.04, -.02]
        if kind == 'pose': item.pose.pose.position.x = .3
        receive(node, kind, item)
    node.publish_control_value()
    assert node.controller_publisher.messages[-1].data == pytest.approx(
        node.controller_obj.saturate_command(GESC+SUPERVISOR))
    assert node.state_value[0] == 0.
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node._v2_admission_tick()
    assert node.state_value[0] == .3
    assert list(node.input_value) == [.04, -.02]
