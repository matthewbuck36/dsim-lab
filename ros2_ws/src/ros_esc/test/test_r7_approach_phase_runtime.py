"""Phase selection through actual candidates, generated guidance and controller.

C01 anchor/first command are retained in r7_approach_feasibility_v1:
input_manifest.json case C01 and trajectories.jsonl line106530. Other evidence
and identities use existing controlled fixtures; this is not a bag replay.
"""
import math
from types import SimpleNamespace

import pytest
from rclpy.time import Time
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray, Timekeeper
from ros_esc.supervisor_node.centered_verification import (
    CENTERED_MODE, tracking_command, tracking_controller)
from ros_esc.supervisor_node.escape_recenter import OperatingBounds, Pose2D
from ros_esc.supervisor_node.state_machine import State
from ros_esc.v2_stream import time_to_ns

import test_centered_verification_runtime as centered
import test_r5_centered_commit_handoff as handoff
import test_v2_controller_motion as motion
import test_v2_supervisor as lifecycle

node_factory = motion.node_factory
centered_node = centered.centered_node
CENTER = (1.188835947139796, .9470764318453091)
POSITION = (1.2783662028258218, .9939938668793433)
YAW = 1.0513878461696335
FIRST_COMMAND = (-.0425847359177483, .27217060185849096)
ACCEPTED_NS, FIRST_NS, POSE_NS = 71_100_000_000, 71_200_000_000, 71_193_000_000


def c01_owner(monkeypatch):
    node, owner = lifecycle.adapter()
    node.run_id = motion.RUN
    owner.centered, owner.verification_mode = True, CENTERED_MODE
    owner.tracking_control = tracking_controller(centered.CONFIG)
    owner.guidance_publisher = lifecycle.Publisher()
    node.event_publisher = lifecycle.Publisher()
    node.supervisor_command_stale_sec = .5
    node.boundary_recovery_trigger_clearance_m = .1
    node.bounds = OperatingBounds()
    node._active_fill_avoidances = lambda: ()
    centered.fresh(owner, ACCEPTED_NS, POSITION, YAW)
    original = owner.confirmation
    def at_center(message):
        message.center_x_m, message.center_y_m = CENTER
        values = list(message.legacy_snapshot)
        values[3:5] = CENTER
        message.legacy_snapshot = values
        original(message)
    with monkeypatch.context() as confirmation:
        confirmation.setattr(owner, 'confirmation', at_center)
        lifecycle.confirm(owner, 'pde_mean_v1')
    assert owner.candidate is not None
    assert lifecycle.step(owner).current == State.VERIFY_EXTREMUM
    node.clock_ns = FIRST_NS
    owner.readiness(Bool(data=True))
    lifecycle.pose(owner, source=POSE_NS, xy=POSITION)
    node.latest_pose = Pose2D(POSE_NS/1e9, *POSITION, YAW)
    return SimpleNamespace(node=node, owner=owner, candidate=owner.candidate)


def publish(case):
    state = motion.state(int(case.node.machine.state), int(State.SEARCH), case.owner.now()/1e9)
    case.owner.publish_guidance(state)
    return state, case.owner.guidance_publisher.messages[-1]


def test_actual_candidate_guidance_matches_nominated_c01_first_command(monkeypatch):
    case = c01_owner(monkeypatch)
    state, message = publish(case)
    assert message.valid and not message.collection_started
    assert (message.linear_x_mps, message.angular_z_radps) == pytest.approx(FIRST_COMMAND, abs=1e-12)
    assert message.state_stamp == state.stamp
    assert time_to_ns(message.pose_stamp) == POSE_NS
    assert time_to_ns(message.accepted_at) == ACCEPTED_NS
    assert time_to_ns(message.command_expires_at) == ACCEPTED_NS+8_000_000_000
    circular = tracking_command(case.owner.tracking_control, CENTER, POSITION, YAW, .1)
    assert circular[[0,5]] == pytest.approx([-.027076491153918924, .19124202572795598])
    assert circular[[0,5]] != pytest.approx(FIRST_COMMAND)


def test_actual_admission_switch_and_reentry_keep_original_acceptance_phase(monkeypatch):
    case = c01_owner(monkeypatch)
    accepted = case.candidate.accepted_ns
    inside = (CENTER[0]+.05, CENTER[1])
    admitted = accepted+2_000_000_000
    centered.fresh(case.owner, admitted, inside, YAW)
    case.owner._admit_collection(case.candidate)
    assert case.candidate.collection_admitted_ns == admitted
    original_end = case.candidate.deadline_ns
    assert original_end == admitted+12_000_000_000
    _, message = publish(case)
    expected = tracking_command(case.owner.tracking_control, CENTER, inside, YAW, 2.)
    assert message.valid and message.collection_started
    assert (message.linear_x_mps, message.angular_z_radps) == pytest.approx(expected[[0,5]])
    reset = tracking_command(case.owner.tracking_control, CENTER, inside, YAW, 0.)
    assert expected[[0,5]] != pytest.approx(reset[[0,5]])
    centered.fresh(case.owner, admitted+100_000_000, (CENTER[0]+.2,CENTER[1]), YAW)
    case.owner._admit_collection(case.candidate)
    centered.fresh(case.owner, admitted+200_000_000, inside, YAW)
    case.owner._admit_collection(case.candidate)
    _, message = publish(case)
    expected = tracking_command(case.owner.tracking_control, CENTER, inside, YAW, 2.2)
    assert (message.linear_x_mps, message.angular_z_radps) == pytest.approx(expected[[0,5]])
    assert case.candidate.accepted_ns == accepted
    assert case.candidate.collection_admitted_ns == admitted
    assert case.candidate.deadline_ns == original_end
    events = [m for m in case.node.event_publisher.messages if m.event_type == 12]
    assert len(events) == 1 and time_to_ns(events[0].stamp) == admitted


@pytest.mark.parametrize('first', ['state', 'guidance'])
def test_actual_controller_commands_the_retained_approach_proposal(monkeypatch, centered_node, first):
    case = c01_owner(monkeypatch)
    state, guidance = publish(case)
    node = centered_node
    node.enable_observability = True
    node.get_clock().set_ros_time_override(Time(nanoseconds=FIRST_NS))
    node.timekeeping_callback(Timekeeper(mode='sim time', start_time=0.))
    pose = motion.pose(POSE_NS/1e9)
    pose.pose.pose.position.x, pose.pose.pose.position.y = POSITION
    pose.pose.pose.orientation.z, pose.pose.pose.orientation.w = math.sin(YAW/2), math.cos(YAW/2)
    node.state_callback(pose)
    node.supervisor_command_callback(motion.command())
    if first == 'guidance':
        node.verification_guidance_callback(guidance)
    node.supervisor_state_callback(state)
    if first == 'state':
        node.verification_guidance_callback(guidance)
    node.input_value_callback(StampedFloat64MultiArray(timestamp=FIRST_NS/1e9, data=[.08,.04]))
    expected = [FIRST_COMMAND[0],0.,0.,0.,0.,FIRST_COMMAND[1]]
    assert not node.algorithm_event_publisher.messages
    assert node.controller_publisher.messages[-1].data == pytest.approx(expected)
    assert node.control_diagnostics_publisher.messages[-1].final_command == pytest.approx(expected)
    assert node._authorized_combination(motion.GESC,motion.SUPERVISOR) == pytest.approx(expected)


def test_activated_design_still_uses_original_circular_law_and_r5_exemption(monkeypatch):
    case = handoff.make_handoff(monkeypatch)
    _, message = handoff.publish(case)
    assert message.valid and message.collection_started
    assert not case.candidate.cancelled and not case.prep.cancelled
    assert (message.linear_x_mps, message.angular_z_radps) == pytest.approx(case.expected[[0,5]])
    assert case.node.machine.state == State.DESIGN_OR_MERGE_FILL
