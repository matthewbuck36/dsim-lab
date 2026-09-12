"""Actual supervisor DESIGN publication revisions and controller diagnostics."""
import json
from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest
from rclpy.parameter import Parameter
from rclpy.time import Time
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.state_machine import State
from ros_esc_interfaces.msg import Timekeeper
import test_centered_verification_runtime as centered
import test_v2_controller_motion as motion
import test_v2_supervisor as lifecycle

node_factory = motion.node_factory
centered_node = centered.centered_node


def test_actual_design_callback_same_tick_guidance_keeps_fresh_authority(centered_node, monkeypatch):
    node = centered_node
    params = {'use_sim_time':True, 'continuous_search_mode':'rolling_gesc_v2',
              'v2_run_id':motion.RUN, 'v2_stream_config_json':json.dumps(lifecycle.config()),
              'convergence_metric_mode':'centroid_windows_v2',
              'extremum_classification_mode':'counted_candidates', 'known_source_count':2,
              'max_fill_clusters':1, 'v2_candidate_radius_m':.75, 'v2_candidate_epsilon_m':.15,
              'v2_verification_motion_mode':centered.CENTERED_MODE,
              'v2_verification_controller_config_filepath':str(centered.CONFIG)}
    supervisor = SupervisorNode(parameter_overrides=[Parameter(k,value=v) for k,v in params.items()])
    try:
        supervisor.clock_ns = 0
        monkeypatch.setattr(supervisor, 'get_clock', lambda: SimpleNamespace(
            now=lambda: Time(nanoseconds=supervisor.clock_ns)))
        monkeypatch.setattr(centered.moving.time, 'monotonic_ns', lambda: 1_000_000_000)
        owner = supervisor.moving_v2
        owner.timekeeper(Timekeeper(mode='sim time',start_time=0.))
        supervisor.state_publisher = lifecycle.Publisher()
        owner.guidance_publisher = lifecycle.Publisher()
        supervisor.event_publisher = lifecycle.Publisher()
        owner.command_publisher = lifecycle.Publisher()
        lifecycle.stream(owner,end=10.)
        centered.fresh(owner,10_000_000_000)
        lifecycle.confirm(owner)
        assert lifecycle.step(owner).current == State.VERIFY_EXTREMUM
        assert lifecycle.step(owner).current == State.DESIGN_OR_MERGE_FILL
        # on_transition emitted DESIGN before PREPARE. This is the timer's final publication.
        supervisor._publish_state_and_command(10.)
        states = supervisor.state_publisher.messages
        messages = owner.guidance_publisher.messages
        assert len(states) == len(messages) == 2 and states[0].stamp == states[1].stamp
        assert messages[0].publication_sequence < messages[1].publication_sequence
        motion.prepare(node, states[0])
        for state, message in zip(states, messages):
            node.supervisor_state_callback(state)
            node.verification_guidance_callback(message)
        assert node._verification_guidance_fault(node.latest_algorithm_state) is None
        assert np.any(node._authorized_combination(motion.GESC,motion.SUPERVISOR))
        assert not messages[0].valid
        assert messages[0].linear_x_mps == messages[0].angular_z_radps == 0.
        assert messages[1].valid
        assert not node.algorithm_event_publisher.messages
    finally:
        supervisor.destroy_node()


def test_centered_control_diagnostics_retain_actual_proposal_and_final_command(centered_node):
    node = centered_node
    node.enable_observability = True
    motion.prepare(node)
    message = centered.guidance(node)
    node.verification_guidance_callback(message)
    diagnostic = node.control_diagnostics_publisher.messages[-1]
    actual = node.controller_publisher.messages[-1].data
    assert diagnostic.final_command_valid and diagnostic.combined_command_unsaturated_valid
    assert diagnostic.final_command == pytest.approx(actual)
    assert diagnostic.combined_command_unsaturated == pytest.approx(actual)
    assert diagnostic.gesc_command_unsaturated_valid and diagnostic.supervisor_contribution_valid
    assert np.asarray(diagnostic.gesc_command_unsaturated)+diagnostic.supervisor_contribution == pytest.approx(actual)
    assert (diagnostic.final_command[0],diagnostic.final_command[5]) == pytest.approx((message.linear_x_mps,message.angular_z_radps))
    assert diagnostic.gesc_command_unsaturated != pytest.approx(actual)


@pytest.mark.parametrize('order', ['state_first','guidance_first'])
def test_distinct_same_tick_state_revisions_require_exact_hash(centered_node, order):
    node = centered_node
    original = motion.state()
    motion.prepare(node, original)
    node.verification_guidance_callback(centered.guidance(node,original))
    revised = deepcopy(original)
    revised.transition_reason = 'new exact state revision at the same clock tick'
    proposal = centered.guidance(node,revised)
    proposal.publication_sequence = 2
    proposal.linear_x_mps = .035
    if order == 'state_first':
        node.supervisor_state_callback(revised)
        assert not np.any(node._authorized_combination(motion.GESC,motion.SUPERVISOR))
        node.verification_guidance_callback(proposal)
    else:
        node.verification_guidance_callback(proposal)
        assert node._authorized_combination(motion.GESC,motion.SUPERVISOR)[0] == -.075
        node.supervisor_state_callback(revised)
    assert node._authorized_combination(motion.GESC,motion.SUPERVISOR)[0] == .035


def test_same_state_guidance_revisions_reject_rollback_and_conflicts(centered_node):
    node = centered_node; motion.prepare(node)
    original = centered.guidance(node)
    node.verification_guidance_callback(original)
    revised = deepcopy(original); revised.publication_sequence = 2; revised.linear_x_mps = .025
    node.verification_guidance_callback(revised)
    assert node._authorized_combination(motion.GESC,motion.SUPERVISOR)[0] == .025
    node.verification_guidance_callback(original)
    assert not np.any(node._authorized_combination(motion.GESC,motion.SUPERVISOR))
    assert 'regressed' in node.verification_guidance_input_fault
    recovery = deepcopy(revised); recovery.publication_sequence = 3
    node.verification_guidance_callback(recovery)
    assert node._authorized_combination(motion.GESC,motion.SUPERVISOR)[0] == .025
    corrupt = deepcopy(recovery); corrupt.linear_x_mps = -.025
    node.verification_guidance_callback(corrupt)
    node.verification_guidance_callback(recovery)
    assert not np.any(node._authorized_combination(motion.GESC,motion.SUPERVISOR))
    assert 'conflicting' in node.verification_guidance_input_fault


def test_guidance_sequence_frontier_survives_clock_authorization_reset(centered_node):
    node = centered_node; motion.prepare(node)
    message = centered.guidance(node); message.publication_sequence = 5
    node.verification_guidance_callback(message)
    frontier = node.verification_guidance_frontier
    node._v2_clear_authorization()
    assert node.verification_guidance_frontier == frontier
