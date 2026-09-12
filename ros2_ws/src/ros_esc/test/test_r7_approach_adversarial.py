"""Fixed-center approach preserves admission, safety and legacy ownership.

Small boundary checks reuse the existing actual supervisor/guidance fixtures.
No trajectory simulator or copy of the tracking formula is introduced.
"""
import math

import pytest
from std_msgs.msg import Bool
from ros_esc.supervisor_node.centered_verification import (
    LEGACY_MODE, tracking_command, tracking_controller)
from ros_esc.supervisor_node.escape_recenter import FillAvoidance, OperatingBounds
from ros_esc.supervisor_node.state_machine import State

import test_centered_verification_runtime as centered
import test_v2_controller_motion as motion


def approaching(monkeypatch, position=(.25, 0.)):
    node, owner = centered.centered_owner(monkeypatch)
    centered.fresh(owner, owner.candidate.accepted_ns+100_000_000, position)
    assert owner.candidate.collection_admitted_ns is None
    return node, owner


def publish(node, owner):
    state = motion.state(int(node.machine.state), stamp=owner.now()/1e9)
    owner.publish_guidance(state)
    return owner.guidance_publisher.messages[-1]


def assert_invalid_zero(message):
    assert not message.valid
    assert message.linear_x_mps == message.angular_z_radps == 0.


@pytest.mark.parametrize('obstruction', ['fill', 'room'])
def test_approach_uses_existing_sweep_and_cannot_cross_an_obstruction(monkeypatch, obstruction):
    node, owner = approaching(monkeypatch)
    candidate = owner.candidate
    original_deadline = candidate.deadline_ns
    if obstruction == 'fill':
        node._active_fill_avoidances = lambda: (FillAvoidance(91, 91, 0., 0., .4),)
    else:
        # The unchanged reverse command from x=.25 crosses this nearby west wall.
        node.bounds = OperatingBounds(x_min=.249, x_max=2., y_min=-2., y_max=2.,
                                      center_x=1., center_y=0., wall_margin=0.)
    message = publish(node, owner)
    assert_invalid_zero(message)
    assert message.reason == 'centered_command_sweep_unsafe'
    assert candidate.cancelled
    assert candidate.deadline_ns == original_deadline
    assert candidate.collection_admitted_ns is None
    assert node.machine.state == State.VERIFY_EXTREMUM


@pytest.mark.parametrize('fault', ['pose_stale', 'readiness', 'departed', 'cancelled'])
def test_approach_cannot_bypass_existing_candidate_and_freshness_guards(monkeypatch, fault):
    node, owner = approaching(monkeypatch)
    candidate = owner.candidate
    accepted, deadline = candidate.accepted_ns, candidate.deadline_ns
    if fault == 'pose_stale':
        node.clock_ns += 500_000_001
    elif fault == 'readiness':
        owner.readiness(Bool(data=False))
    elif fault == 'departed':
        centered.fresh(owner, owner.now()+100_000_000, (owner.radius+.01, 0.))
    else:
        owner.cancel('controlled_candidate_cancellation')
    assert_invalid_zero(publish(node, owner))
    assert candidate.accepted_ns == accepted and candidate.deadline_ns == deadline
    assert candidate.collection_admitted_ns is None
    assert node.machine.state == State.VERIFY_EXTREMUM


@pytest.mark.parametrize('state', [State.SEARCH, State.FAILSAFE])
def test_approach_never_creates_command_authority_outside_verification(monkeypatch, state):
    node, owner = approaching(monkeypatch)
    node.machine.state = state
    message = publish(node, owner)
    assert_invalid_zero(message)
    assert message.reason == 'outside_centered_collection'
    assert owner.candidate.collection_admitted_ns is None


def test_missing_candidate_cannot_publish_a_fixed_center_approach(monkeypatch):
    node, owner = approaching(monkeypatch)
    owner.candidate = None
    assert_invalid_zero(publish(node, owner))


def test_guidance_publication_alone_never_admits_collection_or_restarts_clocks(monkeypatch):
    node, owner = approaching(monkeypatch, position=(.079, 0.))
    candidate = owner.candidate
    original = (candidate.candidate_id, candidate.accepted_ns, candidate.deadline_ns)
    first = publish(node, owner)
    assert first.valid and not first.collection_started
    assert candidate.collection_admitted_ns is None
    centered.fresh(owner, owner.now()+100_000_000, (.079, 0.))
    second = publish(node, owner)
    assert second.valid and not second.collection_started
    assert (second.linear_x_mps, second.angular_z_radps) == pytest.approx(
        (first.linear_x_mps, first.angular_z_radps))
    assert (candidate.candidate_id, candidate.accepted_ns, candidate.deadline_ns) == original
    assert candidate.collection_admitted_ns is None
    assert not node.event_publisher.messages


@pytest.mark.parametrize('fault,approach', [('elapsed', True), ('position', True), ('elapsed', False)])
def test_explicit_phase_selection_preserves_invalid_input_rejection(fault, approach):
    controller = tracking_controller(centered.CONFIG)
    elapsed, position = (-.001, (.25, 0.)) if fault == 'elapsed' else (0., (math.nan, 0.))
    with pytest.raises(ValueError, match='invalid centered tracking input'):
        tracking_command(controller, (0., 0.), position, 0., elapsed, approach=approach)


def test_legacy_direct_call_keeps_its_retained_circular_command_and_opt_in_is_explicit():
    controller = tracking_controller(centered.CONFIG)
    original = tracking_command(controller, (0., 0.), (.25, 0.), 0., 0.)
    explicit = tracking_command(controller, (0., 0.), (.25, 0.), 0., 0., approach=False)
    assert original == pytest.approx(explicit)
    # Golden value retained by the pre-R7 centered controller-law regression.
    assert (original[0], original[5]) == pytest.approx((-.1, .09))


def test_legacy_rolling_mode_still_publishes_no_centered_proposal(monkeypatch):
    node, owner = approaching(monkeypatch)
    owner.centered = False
    owner.verification_mode = LEGACY_MODE
    previous_count = len(owner.guidance_publisher.messages)
    owner.publish_guidance(motion.state(stamp=owner.now()/1e9))
    assert len(owner.guidance_publisher.messages) == previous_count
    assert node.machine.state == State.VERIFY_EXTREMUM
    assert owner.candidate.collection_admitted_ns is None
