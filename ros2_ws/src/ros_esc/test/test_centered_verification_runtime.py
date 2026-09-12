"""Selected centered collection timing and actual controller transport gates."""
from copy import deepcopy
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from rclpy.time import Time
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import AlgorithmState, VerificationGuidance
from ros_esc.supervisor_node import v2_supervisor as moving
from ros_esc.supervisor_node.centered_verification import (
    ADMISSION_DETAIL, CENTERED_MODE, tracking_command, tracking_controller)
from ros_esc.supervisor_node.escape_recenter import OperatingBounds, Pose2D
from ros_esc.supervisor_node.state_machine import State, TransitionInputs
from ros_esc.v2_stream import stream_contract_id, time_to_ns
import test_v2_supervisor as lifecycle
import test_v2_controller_motion as motion

CONFIG = Path(__file__).parents[1]/'ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage_m4_v6_gain_half.json'
node_factory = motion.node_factory


def centered_owner(monkeypatch, *, raw=-3.):
    monkeypatch.setattr(moving.time, 'monotonic_ns', lambda: 1_000_000_000)
    node, owner = lifecycle.adapter()
    owner.centered, owner.verification_mode = True, CENTERED_MODE
    owner.tracking_control = tracking_controller(CONFIG)
    owner.guidance_publisher = lifecycle.Publisher()
    node.event_publisher = lifecycle.Publisher()
    node.supervisor_command_stale_sec = .5
    node.boundary_recovery_trigger_clearance_m = .1
    node.bounds = OperatingBounds()
    node._active_fill_avoidances = lambda: []
    lifecycle.stream(owner, raw=raw)
    lifecycle.confirm(owner)
    assert lifecycle.step(owner).current == State.VERIFY_EXTREMUM
    return node, owner


def fresh(owner, ns, xy=(0., 0.), yaw=0.):
    owner.node.clock_ns = ns
    owner.readiness(Bool(data=True))
    lifecycle.pose(owner, xy=xy)
    owner.node.latest_pose = Pose2D(ns*1e-9, *xy, yaw)


@pytest.mark.parametrize('offset', [0, 7_999_999_999, 8_000_000_000])
def test_first_admission_freezes_exact_clock_and_never_restarts(monkeypatch, offset):
    node, owner = centered_owner(monkeypatch)
    candidate = owner.candidate
    # Avoid replacing the already admitted pose at the same source stamp.
    fresh(owner, candidate.accepted_ns+offset)
    owner._admit_collection(candidate)
    admitted = candidate.accepted_ns+offset
    assert candidate.collection_admitted_ns == admitted
    assert candidate.deadline_ns == min(admitted+12_000_000_000, candidate.accepted_ns+20_000_000_000)
    event = node.event_publisher.messages[-1]
    assert event.event_type == 12 and event.detail == ADMISSION_DETAIL
    assert time_to_ns(event.stamp) == admitted
    assert event.value_names == ['candidate_id', 'search_epoch']
    fresh(owner, admitted+100_000_000, (.2, 0.))
    owner._admit_collection(candidate)
    fresh(owner, admitted+200_000_000)
    owner._admit_collection(candidate)
    assert candidate.collection_admitted_ns == admitted
    assert len(node.event_publisher.messages) == 1


@pytest.mark.parametrize('offset,xy', [(8_000_000_001, (0.,0.)), (8_000_000_000, (.081,0.))])
def test_missed_approach_cancels_without_renewal(monkeypatch, offset, xy):
    node, owner = centered_owner(monkeypatch)
    candidate = owner.candidate
    fresh(owner, candidate.accepted_ns+offset, xy)
    owner.inputs(TransitionInputs())
    assert candidate.collection_admitted_ns is None and candidate.cancelled
    assert candidate.reason == 'centered_approach_deadline'
    assert not node.event_publisher.messages


def test_ready_pretrigger_evidence_cannot_skip_approach_but_is_retained(monkeypatch):
    node, owner = centered_owner(monkeypatch, raw=None)
    candidate = owner.candidate
    fresh(owner, candidate.accepted_ns+100_000_000, (.2, 0.))
    records = len(owner.raw.records)
    assert not owner.inputs(TransitionInputs()).candidate_cost_ready
    assert candidate.snapshot is None
    fresh(owner, candidate.accepted_ns+200_000_000)
    assert owner.inputs(TransitionInputs()).candidate_cost_ready
    assert candidate.snapshot is not None
    assert len(owner.raw.records) == records
    assert time_to_ns(candidate.snapshot.evidence_start) < candidate.collection_admitted_ns


@pytest.mark.parametrize('admission_offset', [100_000_000, 8_000_000_000])
def test_collection_and_total_expiry_are_enforced(monkeypatch, admission_offset):
    _, owner = centered_owner(monkeypatch)
    candidate = owner.candidate
    fresh(owner, candidate.accepted_ns+admission_offset)
    owner._admit_collection(candidate)
    fresh(owner, candidate.deadline_ns)
    owner.inputs(TransitionInputs())
    assert candidate.cancelled and candidate.reason == 'verification_deadline'


@pytest.mark.parametrize('failure', ['departed', 'stale', 'readiness'])
def test_selected_safety_inputs_cancel_immediately(monkeypatch, failure):
    _, owner = centered_owner(monkeypatch)
    candidate = owner.candidate
    fresh(owner, candidate.accepted_ns+100_000_000, (.6, 0.) if failure == 'departed' else (0.,0.))
    if failure == 'stale': owner.node.clock_ns += 500_000_001
    if failure == 'readiness': owner.readiness(Bool(data=False))
    owner.inputs(TransitionInputs())
    assert candidate.cancelled


@pytest.mark.parametrize('yaw,expected', [(0.,(-.1,.09)), (math.pi,(.1,-.09))])
def test_selected_controller_law_preserves_reverse_and_rotation(yaw, expected):
    command = tracking_command(tracking_controller(CONFIG), (0.,0.), (.25,0.), yaw, 0.)
    assert (command[0], command[5]) == pytest.approx(expected)
    assert np.count_nonzero(command[[1,2,3,4]]) == 0


@pytest.mark.parametrize('safe', [True, False, 'exception'])
def test_guidance_uses_existing_reverse_sweep_and_invalid_zero_on_failure(monkeypatch, safe):
    _, owner = centered_owner(monkeypatch)
    fresh(owner, owner.candidate.accepted_ns+100_000_000, (.25,0.))
    seen = []
    def sweep(position, yaw, velocity, *args, **kwargs):
        seen.append((yaw, velocity))
        if safe == 'exception': raise ValueError('invalid geometry')
        return safe
    monkeypatch.setattr('ros_esc.supervisor_node.escape_recenter.command_sweep_is_safe', sweep)
    state = motion.state(stamp=owner.now()*1e-9)
    owner.publish_guidance(state)
    message = owner.guidance_publisher.messages[-1]
    assert seen[0] == pytest.approx((math.pi, .1))
    assert message.state_stamp == state.stamp and message.stamp == state.stamp
    assert message.valid is (safe is True)
    if safe is True:
        assert message.linear_x_mps == -.1
        assert message.run_id == owner.node.run_id and message.stream_contract_id == owner.contract
    else:
        assert owner.candidate.cancelled
        assert message.linear_x_mps == message.angular_z_radps == 0.


@pytest.fixture
def centered_node(node_factory, monkeypatch):
    original = motion.arguments
    def arguments(mode='rolling_gesc_v2'):
        args = original(mode)
        args[5] = str(CONFIG)
        return args+['--v2-verification-motion-mode', CENTERED_MODE,
                     '--v2-stream-config-json', json.dumps(lifecycle.config())]
    monkeypatch.setattr(motion, 'arguments', arguments)
    return node_factory()


def guidance(node, state=None):
    state = state or motion.state()
    msg = VerificationGuidance()
    msg.schema_version = 2
    msg.publication_sequence = 1
    msg.state_sha256 = node._guidance_state_key(state)[1]
    msg.stamp = deepcopy(state.stamp); msg.state_stamp = deepcopy(state.stamp)
    msg.pose_stamp = moving.stamp(10_000_000_000)
    msg.accepted_at = moving.stamp(9_000_000_000)
    msg.verification_expires_at = moving.stamp(17_000_000_000)
    msg.command_expires_at = deepcopy(msg.verification_expires_at)
    msg.run_id = motion.RUN
    msg.stream_contract_id = stream_contract_id(lifecycle.config(), 0)
    msg.frame_id, msg.mode = 'odom', CENTERED_MODE
    msg.search_epoch, msg.candidate_id, msg.algorithm_state = 1, 1, state.state
    msg.linear_x_mps, msg.angular_z_radps, msg.valid = -.075, .15, True
    return msg


@pytest.mark.parametrize('first', ['state', 'guidance'])
def test_actual_controller_exact_companion_allows_both_arrival_orders(centered_node, first):
    node = centered_node
    if first == 'guidance': node.verification_guidance_callback(guidance(node))
    motion.prepare(node)
    if first == 'state':
        assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(np.zeros(6))
        assert not node.algorithm_event_publisher.messages
        node.verification_guidance_callback(guidance(node))
    expected = [-.075,0.,0.,0.,0.,.15]
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(expected)
    assert node.controller_publisher.messages[-1].data == pytest.approx(expected)


@pytest.mark.parametrize('bad', ['run', 'contract', 'frame', 'epoch', 'candidate', 'state', 'stamp',
                                'source', 'expired', 'admission', 'future_admission', 'cap', 'speed', 'invalid', 'nan'])
def test_actual_controller_rejects_bad_guidance(centered_node, bad):
    node = centered_node; motion.prepare(node); msg = guidance(node)
    if bad == 'run': msg.run_id = 'wrong'
    elif bad == 'contract': msg.stream_contract_id = 'b'*64
    elif bad == 'frame': msg.frame_id = 'map'
    elif bad == 'epoch': msg.search_epoch = 0
    elif bad == 'candidate': msg.candidate_id = 0
    elif bad == 'state': msg.algorithm_state = AlgorithmState.STATE_SEARCH
    elif bad == 'stamp': msg.stamp = moving.stamp(9_900_000_000)
    elif bad == 'source': msg.pose_stamp = moving.stamp(9_499_999_999)
    elif bad == 'expired': msg.command_expires_at = moving.stamp(10_000_000_000)
    elif bad == 'admission': msg.collection_admitted_at = moving.stamp(9_500_000_000)
    elif bad == 'future_admission':
        msg.collection_started = True
        msg.collection_admitted_at = moving.stamp(10_100_000_000)
        msg.verification_expires_at = moving.stamp(22_100_000_000)
        msg.command_expires_at = deepcopy(msg.verification_expires_at)
    elif bad == 'cap': msg.verification_expires_at = moving.stamp(30_000_000_000)
    elif bad == 'speed': msg.linear_x_mps = .10001
    elif bad == 'invalid': msg.valid = False
    elif bad == 'nan': msg.angular_z_radps = float('nan')
    node.verification_guidance_callback(msg)
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(np.zeros(6))
    assert node.twist_publisher.messages[-1].linear.x == node.twist_publisher.messages[-1].angular.z == 0.


def test_actual_controller_identical_repeat_cannot_refresh_or_overwrite_conflict(centered_node):
    node = centered_node; motion.prepare(node); msg = guidance(node)
    node.verification_guidance_callback(msg)
    key = node._guidance_state_key(node.latest_algorithm_state)
    receipt = node.verification_guidance[key][1:3]
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node.verification_guidance_callback(msg)
    assert node.verification_guidance[key][1:3] == receipt
    msg.linear_x_mps = .02; node.verification_guidance_callback(msg)
    node.verification_guidance_callback(guidance(node))
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(np.zeros(6))


def test_actual_controller_initial_design_uses_separate_prepare_expiry(centered_node):
    node = centered_node
    state = motion.state(AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
                         AlgorithmState.STATE_VERIFY_EXTREMUM)
    motion.prepare(node, state)
    msg = guidance(node, state)
    msg.collection_started = True
    msg.collection_admitted_at = moving.stamp(9_500_000_000)
    msg.verification_expires_at = moving.stamp(21_500_000_000)
    msg.command_expires_at = moving.stamp(15_000_000_000)
    node.verification_guidance_callback(msg)
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR)[0] == -.075
    # Advancing the exact state requires a fresh companion, never the previous one.
    node.get_clock().set_ros_time_override(Time(nanoseconds=10_100_000_000))
    node.supervisor_state_callback(motion.state(state.state, state.previous_state, 10.1))
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(np.zeros(6))


@pytest.mark.parametrize('source', ['pose', 'receipt', 'steady'])
def test_actual_controller_guidance_expiry_preserves_original_three_clocks(centered_node, source):
    node = centered_node; motion.prepare(node); msg = guidance(node)
    node.verification_guidance_callback(msg)
    key = node._guidance_state_key(node.latest_algorithm_state)
    item = list(node.verification_guidance[key])
    if source == 'pose': item[0].pose_stamp = moving.stamp(9_499_999_999)
    elif source == 'receipt': item[1] -= 500_000_001
    else: item[2] -= 500_000_001
    node.verification_guidance[key] = tuple(item)
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(np.zeros(6))


@pytest.mark.parametrize('selected', [False, True])
def test_actual_supervisor_constructor_and_publication_preserve_explicit_mode(selected):
    import rclpy
    from rclpy.parameter import Parameter
    from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
    rclpy.init(args=[])
    node = None
    params = {'use_sim_time':True, 'continuous_search_mode':'rolling_gesc_v2',
              'v2_run_id':'centered_constructor', 'v2_stream_config_json':json.dumps(lifecycle.config()),
              'extremum_classification_mode':'counted_candidates', 'known_source_count':2,
              'max_fill_clusters':1, 'v2_candidate_radius_m':.75, 'v2_candidate_epsilon_m':.15}
    if selected:
        params.update(v2_verification_motion_mode=CENTERED_MODE,
                      v2_verification_controller_config_filepath=str(CONFIG))
    try:
        node = SupervisorNode(parameter_overrides=[Parameter(k, value=v) for k,v in params.items()])
        assert node.machine.config.verification_max_sec == (20. if selected else 12.)
        assert node.moving_v2.centered is selected
        if selected:
            node.moving_v2.guidance_publisher = lifecycle.Publisher()
            node._publish_state_and_command(0.)
            message = node.moving_v2.guidance_publisher.messages[-1]
            assert not message.valid and message.linear_x_mps == message.angular_z_radps == 0.
        else:
            assert node.moving_v2.guidance_publisher is None
    finally:
        if node is not None: node.destroy_node()
        rclpy.try_shutdown()


@pytest.mark.parametrize('kind,previous', [(0,1),(1,6),(4,3),(5,3),(6,4),(7,2),(8,1),(3,4)])
def test_guidance_never_changes_other_state_command_ownership(centered_node, kind, previous):
    node = centered_node
    state = motion.state(kind, previous)
    motion.prepare(node, state)
    expected = node._authorized_combination(motion.GESC, motion.SUPERVISOR)
    node.verification_guidance_callback(guidance(node, state))
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(expected)
    assert not node._centered_state(state)
