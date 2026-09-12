"""Actual controller callbacks at the retained C01 ordinary lease boundary."""
from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest
from rclpy.time import Time
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray, Timekeeper
from ros_esc.v2_stream import set_time

import test_centered_verification_runtime as centered
import test_v2_controller_motion as motion

node_factory = motion.node_factory
centered_node = centered.centered_node
C01_ACCEPTED_NS = 71_100_000_000
C01_STATE_NS = 79_000_000_000
C01_END_NS = 79_100_000_000
C01_POSE_NS = 78_979_000_000


def setup_expiry(node, *, collection=False, design=False):
    """Original C01 clocks, actual node/messages; no recorded bag is replayed."""
    node.get_clock().set_ros_time_override(Time(nanoseconds=C01_STATE_NS))
    kind = (AlgorithmState.STATE_DESIGN_OR_MERGE_FILL if design
            else AlgorithmState.STATE_VERIFY_EXTREMUM)
    previous = (AlgorithmState.STATE_VERIFY_EXTREMUM if design
                else AlgorithmState.STATE_SEARCH)
    state = motion.state(kind, previous, C01_STATE_NS/1e9)
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=0.))
    node.state_callback(motion.pose(C01_POSE_NS/1e9))
    node.supervisor_command_callback(motion.command())
    node.supervisor_state_callback(state)
    message = centered.guidance(node, state)
    message.publication_sequence = 1581
    set_time(message.pose_stamp, C01_POSE_NS)
    set_time(message.accepted_at, C01_ACCEPTED_NS)
    set_time(message.verification_expires_at, C01_END_NS)
    set_time(message.command_expires_at, C01_END_NS)
    message.center_x_m, message.center_y_m = 1.188835947139796, .9470764318453091
    message.linear_x_mps, message.angular_z_radps = .03356165278409718, .2810398245205688
    if collection or design:
        # A separate ordinary collection expiry, keeping the same state/end.
        set_time(message.accepted_at, 66_100_000_000)
        message.collection_started = True
        set_time(message.collection_admitted_at, 67_100_000_000)
    node.verification_guidance_callback(message)
    node.input_value_callback(StampedFloat64MultiArray(timestamp=79., data=[.08, .04]))
    assert node._robust_fault_reason() is None
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(
        [message.linear_x_mps, 0., 0., 0., 0., message.angular_z_radps])
    assert not node.algorithm_event_publisher.messages
    return SimpleNamespace(node=node, state=state, guidance=message,
        key=node._guidance_state_key(state), deadline_ns=C01_END_NS)


def advance(case, *, stamp_ns=None, trigger='watchdog'):
    now = case.deadline_ns if stamp_ns is None else stamp_ns
    case.node.get_clock().set_ros_time_override(Time(nanoseconds=now))
    if trigger == 'watchdog':
        case.node.watchdog_callback()
    elif trigger == 'filter':
        case.node.input_value_callback(StampedFloat64MultiArray(timestamp=now/1e9, data=[.08, .04]))
    elif trigger == 'clock':
        case.node._v2_admission_tick()
    else:
        raise ValueError(trigger)


def send_search(case, stamp_ns=None):
    now = case.deadline_ns if stamp_ns is None else stamp_ns
    node = case.node
    node.get_clock().set_ros_time_override(Time(nanoseconds=now))
    node.supervisor_state_callback(motion.state(
        AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_VERIFY_EXTREMUM, now/1e9))
    node.input_value_callback(StampedFloat64MultiArray(timestamp=now/1e9, data=[.08, .04]))


def assert_zero(node):
    assert node.controller_publisher.messages[-1].data == pytest.approx(np.zeros(6))
    twist = node.twist_publisher.messages[-1]
    assert [twist.linear.x, twist.linear.y, twist.linear.z,
            twist.angular.x, twist.angular.y, twist.angular.z] == pytest.approx(np.zeros(6))
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(np.zeros(6))


@pytest.mark.parametrize('collection', [False, True])
@pytest.mark.parametrize('trigger', ['watchdog', 'filter', 'clock'])
def test_original_expiry_waits_zero_until_actual_search(centered_node, collection, trigger):
    case = setup_expiry(centered_node, collection=collection)
    advance(case, trigger=trigger)
    assert_zero(case.node)
    assert not case.node.algorithm_event_publisher.messages
    send_search(case)
    assert case.node._robust_fault_reason() is None
    assert np.any(case.node.controller_publisher.messages[-1].data)
    assert case.node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(
        motion.GESC+motion.SUPERVISOR)
    assert not case.node.algorithm_event_publisher.messages


@pytest.mark.parametrize('trigger', ['watchdog', 'filter', 'clock'])
def test_search_before_expiry_keeps_existing_search_owner(centered_node, trigger):
    case = setup_expiry(centered_node)
    send_search(case, case.deadline_ns-1)
    advance(case, trigger=trigger)
    assert case.node._robust_fault_reason() is None
    assert case.node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(
        motion.GESC+motion.SUPERVISOR)
    assert not case.node.algorithm_event_publisher.messages


def test_duplicate_guidance_during_wait_never_refreshes_original_authority(centered_node):
    case = setup_expiry(centered_node)
    original = deepcopy(case.node.verification_guidance[case.key])
    advance(case)
    case.node.verification_guidance_callback(case.guidance)
    assert case.node.verification_guidance[case.key][1:] == original[1:]
    assert case.node.verification_guidance[case.key][0].command_expires_at == original[0].command_expires_at
    assert_zero(case.node)
    assert not case.node.algorithm_event_publisher.messages
    # Original pose freshness ends the wait before expiry+500ms can renew it.
    advance(case, stamp_ns=C01_POSE_NS+500_000_001)
    assert_zero(case.node)
    assert case.node.algorithm_event_publisher.messages


@pytest.mark.parametrize('order', ['state_first', 'guidance_first'])
@pytest.mark.parametrize('admitted_offset_ns', [0, -1])
def test_legal_once_only_admission_delivered_after_approach_expiry(centered_node, order, admitted_offset_ns):
    case = setup_expiry(centered_node)
    advance(case)
    assert_zero(case.node)
    now = case.deadline_ns+50_000_000
    case.node.get_clock().set_ros_time_override(Time(nanoseconds=now))
    state = motion.state(stamp=now/1e9)
    message = deepcopy(case.guidance)
    message.publication_sequence += 1
    message.stamp = deepcopy(state.stamp)
    message.state_stamp = deepcopy(state.stamp)
    message.state_sha256 = case.node._guidance_state_key(state)[1]
    message.collection_started = True
    admitted = case.deadline_ns+admitted_offset_ns
    set_time(message.collection_admitted_at, admitted)
    set_time(message.verification_expires_at, min(admitted+12_000_000_000,
                                                C01_ACCEPTED_NS+20_000_000_000))
    message.command_expires_at = deepcopy(message.verification_expires_at)
    if order == 'state_first':
        case.node.supervisor_state_callback(state)
        case.node.verification_guidance_callback(message)
    else:
        case.node.verification_guidance_callback(message)
        # The old expired command remains zero until its new exact state exists.
        assert_zero(case.node)
        case.node.supervisor_state_callback(state)
    case.node.input_value_callback(StampedFloat64MultiArray(timestamp=now/1e9, data=[.08, .04]))
    assert case.node._robust_fault_reason() is None
    assert not case.node.algorithm_event_publisher.messages
    assert case.node.controller_publisher.messages[-1].data == pytest.approx(
        [message.linear_x_mps, 0., 0., 0., 0., message.angular_z_radps])
