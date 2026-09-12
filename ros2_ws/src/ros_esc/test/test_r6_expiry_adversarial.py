"""Expired VERIFY grants zero-only waiting, never broader fault immunity.

The shared fixture supplies actual generated messages and controller callbacks
at C01's original clocks. Assertions concern emitted commands and fault events.
"""
from copy import deepcopy

import pytest
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import AlgorithmState
from ros_esc.v2_stream import set_time, time_to_ns

import test_v2_controller_motion as motion
from test_r6_verification_expiry_handoff import (
    C01_POSE_NS, advance, assert_zero, centered_node, node_factory, setup_expiry)


@pytest.fixture(autouse=True)
def fixed_steady_clock(monkeypatch):
    # Unit computation time cannot consume a source/receipt authority lease.
    monkeypatch.setattr(motion.controller.time, 'monotonic_ns', lambda: 10_000_000_000)
    monkeypatch.setattr(motion.controller.time, 'monotonic', lambda: 10.)


def assert_hard_zero(node):
    assert_zero(node)
    assert node.algorithm_event_publisher.messages
    assert node.algorithm_event_publisher.messages[-1].event_type == 70


@pytest.mark.parametrize('fault', [
    'run', 'contract', 'frame', 'candidate', 'epoch', 'mode', 'state',
    'source_future', 'invalid', 'linear_bound', 'angular_nonfinite',
    'inconsistent_deadline', 'schema',
])
def test_expiry_wait_does_not_accept_invalid_revised_companion(centered_node, fault):
    case = setup_expiry(centered_node)
    advance(case)
    assert_zero(case.node)
    assert not case.node.algorithm_event_publisher.messages
    message = deepcopy(case.guidance)
    message.publication_sequence += 1
    if fault == 'run':
        message.run_id = 'unrelated_run'
    elif fault == 'contract':
        message.stream_contract_id = '0'*64
    elif fault == 'frame':
        message.frame_id = 'map'
    elif fault == 'candidate':
        message.candidate_id += 1
    elif fault == 'epoch':
        message.search_epoch += 1
    elif fault == 'mode':
        message.mode = 'legacy_gesc_v1'
    elif fault == 'state':
        message.algorithm_state = AlgorithmState.STATE_SEARCH
    elif fault == 'source_future':
        set_time(message.pose_stamp, case.deadline_ns+1)
    elif fault == 'invalid':
        message.valid = False
    elif fault == 'linear_bound':
        message.linear_x_mps = case.node.controller_obj.max_vx+.001
    elif fault == 'angular_nonfinite':
        message.angular_z_radps = float('nan')
    elif fault == 'inconsistent_deadline':
        set_time(message.command_expires_at, case.deadline_ns+1)
    else:
        message.schema_version = 1
    case.node.verification_guidance_callback(message)
    case.node.watchdog_callback()
    assert_hard_zero(case.node)


@pytest.mark.parametrize('trigger', ['watchdog', 'output'])
@pytest.mark.parametrize('fault', [
    'pose_source', 'filter_source', 'pose_steady', 'filter_steady',
    'state_steady', 'command_steady', 'guidance_receipt', 'guidance_steady',
    'origin', 'controller_compatibility',
])
def test_valid_expiry_wait_cannot_short_circuit_other_faults(centered_node, trigger, fault):
    case = setup_expiry(centered_node)
    advance(case)
    assert not case.node.algorithm_event_publisher.messages
    node = case.node
    if fault in ('pose_source', 'filter_source'):
        setattr(node, 'v2_pose_source_ns' if fault == 'pose_source' else 'v2_input_source_ns',
                case.deadline_ns-500_000_001)
    elif fault.endswith('_steady') and not fault.startswith('guidance'):
        node.v2_active_steady[fault.removesuffix('_steady')] -= 500_000_001
    elif fault in ('guidance_receipt', 'guidance_steady'):
        item = list(node.verification_guidance[case.key])
        if fault == 'guidance_receipt':
            item[1] = case.deadline_ns-500_000_001
        else:
            item[2] -= 500_000_001
        node.verification_guidance[case.key] = tuple(item)
    elif fault == 'origin':
        node.v2_origin_fault = True
    else:
        node.robust_controller_compatible = False
    # Use the common output evaluation so no new filter sample
    # legitimately repairs the injected stale filter authority before the check.
    if trigger == 'output':
        node._evaluate_control_safely()
    else:
        node.watchdog_callback()
    assert_hard_zero(node)


@pytest.mark.parametrize('fault', ['run', 'state_valid', 'weights', 'failsafe'])
def test_new_invalid_supervisor_state_is_not_an_ordinary_expiry_wait(centered_node, fault):
    case = setup_expiry(centered_node)
    advance(case)
    message = motion.state(stamp=case.deadline_ns/1e9)
    if fault == 'run':
        message.run_id = 'unrelated_run'
    elif fault == 'state_valid':
        message.state_valid = False
    elif fault == 'weights':
        message.sensor_weight = float('nan')
    else:
        message.failsafe = True
    case.node.supervisor_state_callback(message)
    case.node.watchdog_callback()
    assert_hard_zero(case.node)


@pytest.mark.parametrize('gate', ['false', 'missing', 'stale'])
def test_recording_gate_retains_its_zero_without_latching_policy(centered_node, gate):
    case = setup_expiry(centered_node)
    advance(case)
    node = case.node
    node.recording_ready_required = True
    node.recording_ready = True
    node.recording_ready_receipt_monotonic = 10.
    if gate == 'false':
        node.recording_ready_callback(Bool(data=False))
    elif gate == 'missing':
        node.recording_ready_receipt_monotonic = None
    else:
        node.recording_ready_receipt_monotonic = 10.-node.recording_ready_stale_sec-.01
    node.publish_control_value()
    node.watchdog_callback()
    assert_zero(node)
    assert not node.algorithm_event_publisher.messages


@pytest.mark.parametrize('trigger', ['watchdog', 'filter', 'clock'])
def test_missing_search_transition_hard_faults_at_original_pose_freshness(centered_node, trigger):
    case = setup_expiry(centered_node)
    advance(case)
    assert not case.node.algorithm_event_publisher.messages
    advance(case, stamp_ns=C01_POSE_NS+500_000_001, trigger=trigger)
    assert_hard_zero(case.node)
    assert case.node.latest_algorithm_state.state == AlgorithmState.STATE_VERIFY_EXTREMUM


@pytest.mark.parametrize('trigger', ['watchdog', 'filter', 'clock'])
def test_initial_design_expiry_remains_an_immediate_hard_fault(centered_node, trigger):
    case = setup_expiry(centered_node, design=True)
    advance(case, trigger=trigger)
    assert_hard_zero(case.node)


def test_conflicting_same_sequence_cannot_be_repaired_by_replaying_old_guidance(centered_node):
    case = setup_expiry(centered_node)
    advance(case)
    conflicting = deepcopy(case.guidance)
    conflicting.linear_x_mps *= .5
    case.node.verification_guidance_callback(conflicting)
    assert_hard_zero(case.node)
    case.node.verification_guidance_callback(case.guidance)
    case.node.watchdog_callback()
    assert_hard_zero(case.node)


def test_new_sequence_cannot_renew_accepted_time_and_consistent_approach_deadlines(centered_node):
    case = setup_expiry(centered_node)
    advance(case)
    message = deepcopy(case.guidance)
    message.publication_sequence += 1
    set_time(message.accepted_at, time_to_ns(message.accepted_at)+100_000_000)
    set_time(message.verification_expires_at, case.deadline_ns+100_000_000)
    set_time(message.command_expires_at, case.deadline_ns+100_000_000)
    case.node.verification_guidance_callback(message)
    case.node.watchdog_callback()
    assert_hard_zero(case.node)


def phase_revision(case, *, accepted_ns, admitted_ns, state_ns):
    """A fresh exact-state phase publication, using only existing wire fields."""
    state = motion.state(stamp=state_ns/1e9)
    message = deepcopy(case.guidance)
    message.publication_sequence += 1
    message.stamp = deepcopy(state.stamp)
    message.state_stamp = deepcopy(state.stamp)
    message.state_sha256 = case.node._guidance_state_key(state)[1]
    message.collection_started = True
    set_time(message.accepted_at, accepted_ns)
    set_time(message.collection_admitted_at, admitted_ns)
    end = min(admitted_ns+12_000_000_000, accepted_ns+20_000_000_000)
    set_time(message.verification_expires_at, end)
    set_time(message.command_expires_at, end)
    return state, message


@pytest.mark.parametrize('fault', ['changed_accepted', 'post_deadline_admission', 'changed_admission'])
def test_new_phase_authority_cannot_rewrite_original_candidate_or_admission(centered_node, fault):
    case = setup_expiry(centered_node, collection=fault == 'changed_admission')
    advance(case)
    new_state_ns = case.deadline_ns+100_000_000
    advance(case, stamp_ns=new_state_ns)
    accepted = time_to_ns(case.guidance.accepted_at)
    admitted = case.deadline_ns
    if fault == 'changed_accepted':
        accepted += 1
    elif fault == 'post_deadline_admission':
        admitted += 1
    else:
        admitted = time_to_ns(case.guidance.collection_admitted_at)+200_000_000
    state, message = phase_revision(case, accepted_ns=accepted, admitted_ns=admitted,
                                    state_ns=new_state_ns)
    case.node.supervisor_state_callback(state)
    case.node.verification_guidance_callback(message)
    case.node.watchdog_callback()
    assert_hard_zero(case.node)
