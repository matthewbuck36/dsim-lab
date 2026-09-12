"""Actual activation/publication handoff with retained C geometry.

Times and raw evidence are controlled existing unit fixtures, not a historical
bag replay. Only the small recorded candidate/fill geometry is bound below.
"""
from copy import deepcopy
from types import MethodType, SimpleNamespace

import numpy as np
import pytest
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import FillCommand, GescDirectionDiagnostics, ObjectiveCostSample
from ros_esc.supervisor_node.centered_verification import CENTERED_MODE, tracking_command, tracking_controller
from ros_esc.supervisor_node.escape_recenter import OperatingBounds
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.state_machine import State
from ros_esc.v2_lifecycle import fill_registry_digest, result_sha256
import test_centered_verification_runtime as centered
import test_v2_controller_motion as motion
import test_v2_supervisor as lifecycle

C_CENTER = (1.1511351182244869, 1.179704057497771)
C_FILL_GEOMETRY = dict(center_x=1.1585728442974839, center_y=1.1586903718453991,
    amplitude=.1, covariance_xx=.2562499999999999, covariance_xy=0.,
    covariance_yy=.2562499999999999, sigma_major=.5062114182829146,
    sigma_minor=.5062114182829146, support_radius=1.518634254848744,
    exit_radius=1.3667708293638696)
# This finite pose points the unchanged tracking law inward through the fill.
# It is a controlled fixture, not an invented rejected-command observation.
HANDOFF_POSE = (C_CENTER[0]-.04, C_CENTER[1])
node_factory = motion.node_factory
centered_node = centered.centered_node


def public_state(case):
    state = motion.state(int(case.node.machine.state), int(State.VERIFY_EXTREMUM),
                         case.owner.now()*1e-9)
    state.active_fill_count = len(case.owner.active_fills)
    state.active_fill_count_valid = True
    return state


def make_handoff(monkeypatch, *, activate=True):
    """Return node/owner/candidate/prep/activation at fresh ROS10s, before publish."""
    monkeypatch.setattr(centered.moving.time, 'monotonic_ns', lambda: 1_000_000_000)
    node, owner = lifecycle.adapter()
    node.run_id = motion.RUN
    owner.centered, owner.verification_mode = True, CENTERED_MODE
    owner.tracking_control = tracking_controller(centered.CONFIG)
    owner.guidance_publisher = lifecycle.Publisher()
    node.event_publisher = lifecycle.Publisher()
    node.supervisor_command_stale_sec = .5
    node.boundary_recovery_trigger_clearance_m = .1
    node.bounds = OperatingBounds()
    node.active_fill_records, node.fill_avoidance_margin_m = {}, .1
    node.moving_v2, node.stationary_centroid = owner, None
    node.fill_callback = MethodType(SupervisorNode.fill_callback, node)
    node._active_fill_avoidances = MethodType(SupervisorNode._active_fill_avoidances, node)
    original_observation, original_pose = lifecycle.observation, lifecycle.pose
    with monkeypatch.context() as translated:
        translated.setattr(lifecycle, 'observation', lambda t, raw=None:
            original_observation(t, raw=raw, xy=C_CENTER))
        translated.setattr(lifecycle, 'pose', lambda owner, source=None, xy=C_CENTER:
            original_pose(owner, source, xy))
        lifecycle.stream(owner)
    centered.fresh(owner, 9_100_000_000, C_CENTER)
    original_confirmation = owner.confirmation
    def confirm_at_center(message):
        message.center_x_m, message.center_y_m = C_CENTER
        values = list(message.legacy_snapshot)
        values[3:5] = C_CENTER
        message.legacy_snapshot = values
        original_confirmation(message)
    with monkeypatch.context() as confirmation:
        confirmation.setattr(owner, 'confirmation', confirm_at_center)
        lifecycle.confirm(owner, 'pde_mean_v1')
    assert lifecycle.step(owner).current == State.VERIFY_EXTREMUM
    assert lifecycle.step(owner).current == State.DESIGN_OR_MERGE_FILL
    prep = owner.current_preparation
    centered.fresh(owner, 9_800_000_000, HANDOFF_POSE)
    lifecycle.prepared(owner, prep)
    centered.fresh(owner, 9_900_000_000, HANDOFF_POSE)
    activation = lifecycle.committed(owner, prep)
    for key, value in C_FILL_GEOMETRY.items():
        setattr(activation.fill, key, value)
    activation.registry_digest_after = fill_registry_digest([activation.fill])
    activation.committed_sha256 = result_sha256(activation)
    if activate:
        owner.result(activation)
        assert prep.activated is not None and node.machine.active_fill_count == 1
    centered.fresh(owner, 10_000_000_000, HANDOFF_POSE)
    expected = tracking_command(owner.tracking_control, C_CENTER, HANDOFF_POSE, 0.,
                                (owner.now()-owner.candidate.accepted_ns)*1e-9)
    assert expected[0] > 0 and expected[5] != 0
    return SimpleNamespace(node=node, owner=owner, candidate=owner.candidate,
                           prep=prep, activation=activation, expected=expected)


def publish(case):
    state = public_state(case)
    case.owner.publish_guidance(state)
    return state, case.owner.guidance_publisher.messages[-1]


def send_ack(case, kind, *, digest=None, source_ns=None):
    owner = case.owner
    message = lifecycle.identity(owner,
        ObjectiveCostSample() if kind == 'objective' else GescDirectionDiagnostics())
    message.registry_digest = digest if digest is not None else case.activation.registry_digest_after
    if source_ns is not None:
        message.stamp = lifecycle.stamp(source_ns)
    if kind == 'objective':
        message.valid = True
        owner.objective(message)
    else:
        message.algorithm_state = int(owner.node.machine.state)
        message.algorithm_state_valid = True
        owner.direction(message)


def test_matching_activation_keeps_identical_nonzero_centered_proposal(monkeypatch):
    case = make_handoff(monkeypatch)
    state, message = publish(case)
    assert message.valid and not case.candidate.cancelled and not case.prep.cancelled
    assert (message.linear_x_mps, message.angular_z_radps) == pytest.approx(case.expected[[0,5]])
    assert message.stamp == state.stamp and message.state_stamp == state.stamp
    assert case.owner.command_publisher.messages[-1].operation == FillCommand.ACTIVATE
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL


@pytest.mark.parametrize('kind,previous', [(State.VERIFY_EXTREMUM, State.SEARCH),
    (State.DESIGN_OR_MERGE_FILL, State.ESCAPE_REPULSE)])
def test_supplied_noninitial_design_state_cannot_borrow_machine_exemption(monkeypatch, kind, previous):
    case = make_handoff(monkeypatch)
    state = public_state(case)
    state.state, state.previous_state = int(kind), int(previous)
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL
    case.owner.publish_guidance(state)
    message = case.owner.guidance_publisher.messages[-1]
    assert not message.valid and message.reason == 'centered_command_sweep_unsafe'
    assert case.candidate.cancelled


@pytest.mark.parametrize('first', ['objective', 'direction'])
def test_only_both_fresh_registry_acks_authorize_escape(monkeypatch, first):
    case = make_handoff(monkeypatch)
    original_expiry = deepcopy(case.prep.command.expires_at)
    publish(case)
    assert lifecycle.step(case.owner) is None
    send_ack(case, first)
    assert lifecycle.step(case.owner) is None
    send_ack(case, 'direction' if first == 'objective' else 'objective')
    transition = lifecycle.step(case.owner)
    assert transition.current == State.ESCAPE_REPULSE
    assert transition.reason == 'typed fill committed and objective acknowledged'
    assert case.prep.command.expires_at == original_expiry
    assert case.node.machine.active_escape_fill_id == case.activation.fill.fill_id


@pytest.mark.parametrize('first', ['state', 'guidance'])
def test_postcommit_actual_controller_retains_guidance_and_final_command(monkeypatch, centered_node, first):
    case = make_handoff(monkeypatch)
    state, message = publish(case)
    node = centered_node
    node.enable_observability = True
    original_pose = motion.pose
    def matching_pose(stamp=10.):
        pose = original_pose(stamp)
        pose.pose.pose.position.x, pose.pose.pose.position.y = HANDOFF_POSE
        return pose
    monkeypatch.setattr(motion, 'pose', matching_pose)
    if first == 'guidance':
        node.verification_guidance_callback(message)
    motion.prepare(node, state)
    if first == 'state':
        node.verification_guidance_callback(message)
    assert not node.algorithm_event_publisher.messages
    assert node._verification_guidance_fault(node.latest_algorithm_state) is None
    expected = case.expected
    assert node._authorized_combination(motion.GESC, motion.SUPERVISOR) == pytest.approx(expected)
    assert node.controller_publisher.messages[-1].data == pytest.approx(expected)
    diagnostic = node.control_diagnostics_publisher.messages[-1]
    assert diagnostic.final_command == pytest.approx(expected)
    assert diagnostic.combined_command_unsaturated == pytest.approx(expected)
    assert np.any(expected)
