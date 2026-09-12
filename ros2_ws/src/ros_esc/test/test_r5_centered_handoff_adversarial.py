"""The current ACTIVATED fill exemption grants no broader motion authority.

Use the shared real-supervisor handoff fixture and actual geometry/ACK owners.
No detector, controller law, lease or registry acceptance is replaced here.
"""
from copy import copy, deepcopy

import pytest
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import FillResult
from ros_esc.supervisor_node.centered_verification import LEGACY_MODE
from ros_esc.supervisor_node.escape_recenter import FillAvoidance, OperatingBounds
from ros_esc.supervisor_node.state_machine import State, TransitionInputs
from ros_esc.v2_stream import time_to_ns

import test_centered_verification_runtime as centered
import test_v2_supervisor as lifecycle
from test_r5_centered_commit_handoff import (
    HANDOFF_POSE, make_handoff, publish, public_state, send_ack)


IDENTITY_MISMATCHES = (
    'candidate_object', 'candidate_id', 'preparation_object',
    'preparation_registration', 'preparation_id', 'preparation_candidate',
    'command_candidate_id', 'prepared_only', 'activation_kind',
    'activation_hash', 'generation', 'registry_digest',
    'activated_generation', 'activated_digest', 'active_fill_id',
    'active_cluster_id', 'active_revision', 'inactive_fill', 'superseded_fill',
    'node_fill_id', 'node_revision', 'node_cluster_key',
    'candidate_cancelled', 'preparation_cancelled', 'redesign', 'return_state',
)


def break_identity(case, mismatch):
    """Alter one retained authority while leaving the obstructing fill present."""
    owner, prep = case.owner, case.prep
    cluster = case.activation.fill.cluster_id
    if mismatch == 'candidate_object':
        owner.candidate = copy(case.candidate)
    elif mismatch == 'candidate_id':
        case.candidate.candidate_id += 1
    elif mismatch == 'preparation_object':
        owner.current_preparation = copy(prep)
    elif mismatch == 'preparation_registration':
        owner.preparations[prep.command.preparation_id] = copy(prep)
    elif mismatch == 'preparation_id':
        prep.command.preparation_id += 1
    elif mismatch == 'preparation_candidate':
        prep.candidate = copy(case.candidate)
    elif mismatch == 'command_candidate_id':
        prep.command.candidate_id += 1
    elif mismatch == 'prepared_only':
        prep.activated = None
        assert prep.prepared.result == FillResult.PREPARED
    elif mismatch == 'activation_kind':
        prep.activated.result = FillResult.PREPARED
    elif mismatch == 'activation_hash':
        prep.activated.committed_sha256 = '0' * 64
    elif mismatch == 'generation':
        owner.generation += 1
    elif mismatch == 'registry_digest':
        owner.registry_digest = '0' * 64
    elif mismatch == 'activated_generation':
        prep.activated.registry_generation += 1
    elif mismatch == 'activated_digest':
        prep.activated.registry_digest_after = '0' * 64
    elif mismatch == 'active_fill_id':
        owner.active_fills[cluster].fill_id += 1
    elif mismatch == 'active_cluster_id':
        owner.active_fills[cluster].cluster_id += 1
    elif mismatch == 'active_revision':
        owner.active_fills[cluster].revision += 1
    elif mismatch == 'inactive_fill':
        owner.active_fills[cluster].active = False
    elif mismatch == 'superseded_fill':
        owner.active_fills[cluster].superseded = True
    elif mismatch == 'node_fill_id':
        case.node.active_fill_records[cluster]['fill_id'] += 1
    elif mismatch == 'node_revision':
        case.node.active_fill_records[cluster]['revision'] += 1
    elif mismatch == 'node_cluster_key':
        case.node.active_fill_records[cluster + 1] = case.node.active_fill_records.pop(cluster)
    elif mismatch == 'candidate_cancelled':
        case.candidate.cancelled = True
    elif mismatch == 'preparation_cancelled':
        prep.cancelled = True
    elif mismatch == 'redesign':
        prep.command.redesign = True
    elif mismatch == 'return_state':
        prep.command.return_state = int(State.ESCAPE_ASSIST)
    else:
        raise AssertionError(mismatch)


@pytest.mark.parametrize('mismatch', IDENTITY_MISMATCHES)
def test_noncurrent_or_unauthenticated_activation_keeps_full_avoidance(monkeypatch, mismatch):
    case = make_handoff(monkeypatch)
    # An accepted ACTIVATED result is terminal; terminal is not cancellation.
    assert case.prep.terminal and case.prep.activated is not None
    break_identity(case, mismatch)
    full = case.node._active_fill_avoidances()
    assert len(full) == 1
    selected = case.owner._centered_handoff_avoidances(case.owner.candidate, case.owner.now())
    assert tuple(selected) == tuple(full)
    # Selection must not rewrite registry facts or acquire command ownership.
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL
    assert case.node.machine.active_fill_count == 1
    assert not case.owner.guidance_publisher.messages


@pytest.mark.parametrize('mismatch', ['node_revision', 'generation', 'activation_hash'])
def test_invalid_identity_reaches_actual_sweep_and_cancels(monkeypatch, mismatch):
    case = make_handoff(monkeypatch)
    break_identity(case, mismatch)
    _, guidance = publish(case)
    assert not guidance.valid
    assert guidance.reason == 'centered_command_sweep_unsafe'
    assert guidance.linear_x_mps == guidance.angular_z_radps == 0.
    assert case.candidate.cancelled and case.prep.cancelled
    assert case.node.machine.active_fill_count == 1


def test_prepared_without_admitted_activation_cannot_hide_an_obstructing_fill(monkeypatch):
    case = make_handoff(monkeypatch, activate=False)
    assert case.prep.prepared is not None and case.prep.activated is None
    # A node-side publication alone cannot supply the missing typed acceptance.
    case.node.fill_callback(case.activation.fill, authoritative=True)
    assert not case.owner.active_fills and case.owner.generation == 0
    full = case.node._active_fill_avoidances()
    assert len(full) == 1
    assert tuple(case.owner._centered_handoff_avoidances(case.candidate, case.owner.now())) == tuple(full)
    _, guidance = publish(case)
    assert not guidance.valid and case.candidate.cancelled


@pytest.mark.parametrize('offset', [0, 1])
def test_original_preparation_lease_has_no_activation_renewal(monkeypatch, offset):
    case = make_handoff(monkeypatch)
    original_expiry = deepcopy(case.prep.command.expires_at)
    expiry = time_to_ns(original_expiry)
    centered.fresh(case.owner, expiry + offset, HANDOFF_POSE)
    full = case.node._active_fill_avoidances()
    assert tuple(case.owner._centered_handoff_avoidances(case.candidate, case.owner.now())) == tuple(full)
    _, guidance = publish(case)
    assert not guidance.valid
    assert time_to_ns(guidance.command_expires_at) == expiry
    assert case.prep.command.expires_at == original_expiry
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL


def test_unrelated_obstructing_fill_survives_current_fill_exemption(monkeypatch):
    case = make_handoff(monkeypatch)
    full = case.node._active_fill_avoidances()
    current = full[0]
    unrelated = FillAvoidance(99, 99, current.center_x, current.center_y, current.radius)
    monkeypatch.setattr(case.node, '_active_fill_avoidances', lambda: full + (unrelated,))
    selected = case.owner._centered_handoff_avoidances(case.candidate, case.owner.now())
    assert tuple(selected) == (unrelated,)
    _, guidance = publish(case)
    assert not guidance.valid and guidance.reason == 'centered_command_sweep_unsafe'
    assert case.candidate.cancelled


def test_room_boundary_still_blocks_the_unchanged_nonzero_tracking_command(monkeypatch):
    case = make_handoff(monkeypatch)
    x, y = HANDOFF_POSE
    # The current positive-x proposal crosses this nearby physical east wall.
    case.node.bounds = OperatingBounds(x_min=x-2., x_max=x+.001,
        y_min=y-2., y_max=y+2., center_x=x-.5, center_y=y, wall_margin=0.)
    assert not case.owner._centered_handoff_avoidances(case.candidate, case.owner.now())
    _, guidance = publish(case)
    assert not guidance.valid and guidance.reason == 'centered_command_sweep_unsafe'
    assert case.candidate.cancelled
    assert guidance.linear_x_mps == guidance.angular_z_radps == 0.


@pytest.mark.parametrize('fault', ['pose_source_stale', 'pose_steady_stale', 'readiness_false', 'departed'])
def test_accepted_activation_never_bypasses_pose_or_readiness_admission(monkeypatch, fault):
    case = make_handoff(monkeypatch)
    if fault == 'pose_source_stale':
        case.node.clock_ns += 500_000_001
    elif fault == 'pose_steady_stale':
        stamp_ns, xy, receipt_ns, steady_ns = case.owner.pose
        case.owner.pose = (stamp_ns, xy, receipt_ns, steady_ns-500_000_001)
    elif fault == 'readiness_false':
        case.owner.readiness(Bool(data=False))
    else:
        center = case.owner.center(case.candidate)
        centered.fresh(case.owner, case.owner.now()+1, (center[0]+case.owner.radius+.01, center[1]))
    _, guidance = publish(case)
    assert not guidance.valid
    assert guidance.linear_x_mps == guidance.angular_z_radps == 0.
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL
    assert case.owner.inputs(TransitionInputs()).fill_result != 'success'


@pytest.mark.parametrize('kind', ['objective', 'direction'])
@pytest.mark.parametrize('fault', ['wrong_digest', 'precommit_source', 'stale_source', 'stale_receipt', 'stale_steady'])
def test_original_ack_identity_and_three_freshness_clocks_still_gate_escape(monkeypatch, kind, fault):
    case = make_handoff(monkeypatch)
    if fault.startswith('stale'):
        centered.fresh(case.owner, case.owner.now()+1_000_000_000, HANDOFF_POSE)
    other = 'direction' if kind == 'objective' else 'objective'
    send_ack(case, other)
    if fault == 'wrong_digest':
        send_ack(case, kind, digest='0'*64)
    elif fault == 'precommit_source':
        send_ack(case, kind, source_ns=time_to_ns(case.activation.committed_at)-1)
    elif fault == 'stale_source':
        send_ack(case, kind, source_ns=case.owner.now()-500_000_001)
    else:
        send_ack(case, kind)
        attribute = kind + '_ack'
        digest, source, receipt, steady = getattr(case.owner, attribute)
        if fault == 'stale_receipt':
            receipt = case.owner.now()-500_000_001
        else:
            steady -= 500_000_001
        setattr(case.owner, attribute, (digest, source, receipt, steady))
    _, guidance = publish(case)
    assert guidance.valid and not case.candidate.cancelled
    assert lifecycle.step(case.owner) is None
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL
    # Fresh acknowledgements through the original callbacks release the same fill.
    send_ack(case, 'objective')
    send_ack(case, 'direction')
    assert lifecycle.step(case.owner).current == State.ESCAPE_REPULSE
    assert case.node.machine.active_escape_fill_id == case.activation.fill.fill_id


@pytest.mark.parametrize('state', [State.SEARCH, State.VERIFY_EXTREMUM, State.ESCAPE_REPULSE,
                                 State.ESCAPE_ASSIST, State.GOAL_HOLD, State.FAILSAFE])
def test_exception_is_unavailable_outside_initial_design(monkeypatch, state):
    case = make_handoff(monkeypatch)
    case.node.machine.state = state
    full = case.node._active_fill_avoidances()
    assert tuple(case.owner._centered_handoff_avoidances(case.candidate, case.owner.now())) == tuple(full)


def test_redesign_and_legacy_keep_existing_command_ownership(monkeypatch):
    case = make_handoff(monkeypatch)
    case.node.machine.design_returns_to_assist = True
    full = case.node._active_fill_avoidances()
    assert tuple(case.owner._centered_handoff_avoidances(case.candidate, case.owner.now())) == tuple(full)
    _, guidance = publish(case)
    assert not guidance.valid and guidance.reason == 'outside_centered_collection'
    assert not case.candidate.cancelled
    case.owner.centered = False
    case.owner.verification_mode = LEGACY_MODE
    before = len(case.owner.guidance_publisher.messages)
    case.owner.publish_guidance(public_state(case))
    assert len(case.owner.guidance_publisher.messages) == before
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL
