"""Actual supervisor callbacks and raw owner under the opt-in trapping policy."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import math
import pytest
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import RecurrentCandidateSnapshot, RecurrentFillCommand, Timekeeper
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor
from ros_esc.supervisor_node.moving_evidence import MovingRawEvidence, snapshot_raw_evidence
from ros_esc.supervisor_node.state_machine import State, TransitionInputs
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc.v2_lifecycle import message_payload, recurrent_snapshot_sha256, snapshot_sha256
from test_r21_trapping_nomination import nomination
import test_v2_supervisor as legacy
from test_v2_moving_evidence import feed, ready

CONFIG = Path(__file__).parents[1]/'ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage_m4_v6_gain_half.json'


def selected_owner(monkeypatch, *, raw=-3., stream_start=51., stream_end=60.):
    steady = [1_000_000_000]
    monkeypatch.setattr('ros_esc.supervisor_node.v2_supervisor.time.monotonic_ns', lambda: steady[0])
    node = legacy.Node()
    node.machine.config = replace(node.machine.config, verification_evidence_policy='recurrent_trapping_v1')
    params = {'v2_verification_motion_mode': 'centered_tracking_v1',
              'v2_verification_controller_config_filepath': str(CONFIG),
              'convergence_metric_mode': 'recurrent_geometry_v3',
              'recording_ready_required': True, 'recording_ready_stale_sec': .5,
              'recording_ready_topic': '/ready', 'v2_direction_diagnostics_topic': '/direction'}
    node.get_parameter = lambda name: SimpleNamespace(value=params[name])
    node.publisher_bindings = []
    def publisher(kind, topic, qos):
        node.publisher_bindings.append((kind, topic))
        return legacy.Publisher()
    node.create_publisher = publisher
    node.event_publisher = legacy.Publisher()
    owner = MovingSupervisor(node, legacy.config(), .5, .1)
    node.adapter = owner
    owner.timekeeper(Timekeeper(mode='sim time', start_time=0.))
    owner.readiness(Bool(data=True))
    legacy.stream(owner, start=stream_start, end=stream_end, raw=raw)
    node.clock_ns = 60_100_000_000
    owner.readiness(Bool(data=True)); legacy.pose(owner)
    owner.publish_context()
    confirmation, diagnostic = nomination(origin_ns=0)
    confirmation = legacy.identity(owner, confirmation)
    confirmation.search_epoch = owner.epoch
    confirmation.context_sequence = owner.context_sequence
    diagnostic.run_id = node.run_id
    diagnostic.source_pose_topic = owner.config['pose_topic']
    confirmation.center_x_m = confirmation.center_y_m = 0.
    diagnostic.center_x_m = diagnostic.center_y_m = 0.
    diagnostic.arc_center_x_m = diagnostic.arc_center_y_m = [0., 0.]
    return SimpleNamespace(node=node, owner=owner, confirmation=confirmation,
                           diagnostic=diagnostic, steady=steady)


def deliver(case, order=('confirmation', 'diagnostic')):
    for kind in order:
        callback = case.owner.confirmation if kind == 'confirmation' else case.owner.recurrent_diagnostic
        callback(getattr(case, kind))


@pytest.mark.parametrize('order', [('confirmation', 'diagnostic'), ('diagnostic', 'confirmation')])
def test_both_orders_freeze_detached_proof_and_accept_without_faking_angular_information(monkeypatch, order):
    case = selected_owner(monkeypatch)
    deliver(case, order)
    owner = case.owner
    assert owner.candidate_sequence == 1 and owner.candidate is not None
    case.diagnostic.center_x_m = 9.  # transport object cannot mutate retained proof
    assert owner.candidate.recurrent_diagnostic.center_x_m == 0.
    assert legacy.step(owner).current == State.VERIFY_EXTREMUM
    inputs = owner.inputs(TransitionInputs())
    assert inputs.candidate_cost_ready and inputs.candidate_verification_passed
    assert not inputs.candidate_informative
    assert owner.candidate.snapshot is not None
    wrapper = owner.snapshot_publisher.messages[-1]
    assert isinstance(wrapper, RecurrentCandidateSnapshot)
    assert not wrapper.snapshot.informative
    assert snapshot_raw_evidence(wrapper.snapshot, evidence_policy='recurrent_trapping_v1').ready
    assert wrapper.snapshot.evidence_sha256 == recurrent_snapshot_sha256(wrapper.snapshot, wrapper)
    assert wrapper.snapshot.evidence_sha256 != snapshot_sha256(wrapper.snapshot)
    assert all(topic not in ('/gesc_gaussian/v2/candidate_snapshots', '/gesc_gaussian/v2/fill_commands')
               for _, topic in case.node.publisher_bindings)


@pytest.mark.parametrize('kind', ['confirmation', 'diagnostic'])
def test_missing_companion_or_expired_original_duplicate_never_allocates(monkeypatch, kind):
    case = selected_owner(monkeypatch)
    deliver(case, (kind,))
    original = deepcopy(case.owner.pending_nominations)
    case.node.clock_ns += 400_000_000
    case.steady[0] += 400_000_000
    deliver(case, (kind,))
    assert case.owner.pending_nominations.keys() == original.keys()
    stored = next(iter(case.owner.pending_nominations.values()))[kind]
    assert stored[2:] == next(iter(original.values()))[kind][2:]
    case.node.clock_ns += 100_000_001
    case.steady[0] += 100_000_001
    case.owner.readiness(Bool(data=True))
    deliver(case)
    assert case.owner.candidate is None and case.owner.accepted_epoch is None


@pytest.mark.parametrize('after_join', [False, True])
def test_conflicting_certificate_is_sticky_and_revokes_original_candidate(monkeypatch, after_join):
    case = selected_owner(monkeypatch)
    deliver(case, ('diagnostic',))
    if after_join:
        deliver(case, ('confirmation',))
    bad = deepcopy(case.diagnostic); bad.center_x_m = .01
    case.owner.recurrent_diagnostic(bad)
    deliver(case)
    assert case.owner.nomination_fault
    assert case.owner.candidate is None or case.owner.candidate.cancelled


@pytest.mark.parametrize('fault', ['readiness', 'state', 'context', 'persistence', 'wrong_epoch'])
def test_interrupted_or_nonsearch_authority_cannot_nominate(monkeypatch, fault):
    case = selected_owner(monkeypatch)
    if fault == 'readiness':
        case.owner.readiness(Bool(data=False)); case.owner.readiness(Bool(data=True))
    elif fault == 'state':
        case.node.machine.state = State.ESCAPE_REPULSE
    elif fault == 'context':
        case.owner.contexts.clear()
    elif fault == 'persistence':
        set_time(case.diagnostic.persistence_start, 0)
    else:
        case.confirmation.search_epoch += 1
    deliver(case)
    assert case.owner.candidate is None and case.owner.accepted_epoch is None


def test_nomination_queue_capacity_is_fail_closed(monkeypatch):
    case = selected_owner(monkeypatch)
    for sequence in range(1, 10):
        msg = deepcopy(case.confirmation); msg.confirmation_sequence = sequence
        case.owner.confirmation(msg)
    deliver(case)
    assert case.owner.nomination_fault and case.owner.candidate is None


def test_prepare_and_cancel_keep_same_certificate_and_nested_evidence_identity(monkeypatch):
    case = selected_owner(monkeypatch)
    deliver(case)
    assert legacy.step(case.owner).current == State.VERIFY_EXTREMUM
    case.owner.inputs(TransitionInputs())
    case.node.machine.state = State.DESIGN_OR_MERGE_FILL
    case.owner.begin_preparation(redesign=False)
    case.owner.cancel('test_cancel')
    messages = case.owner.command_publisher.messages
    assert len(messages) == 2 and all(isinstance(m, RecurrentFillCommand) for m in messages)
    assert [m.command.operation for m in messages] == [1, 3]
    assert messages[0].command.evidence_sha256 == messages[1].command.evidence_sha256
    for field in ('confirmation', 'diagnostic'):
        assert message_payload(getattr(messages[0], field)) == message_payload(getattr(messages[1], field))


@pytest.mark.parametrize('cost,expected', [(-3., True), (0., False), (3., False)])
def test_selected_raw_quality_does_not_turn_a_negative_constant_into_angular_information(cost, expected):
    core = MovingRawEvidence(); core.start_epoch(1, 0)
    feed(core, cost=lambda t: cost)
    old = ready(core)
    selected = ready(core, evidence_policy='recurrent_trapping_v1')
    assert not old.ready and not old.informative
    assert selected.ready == expected and not selected.informative


@pytest.mark.parametrize('tamper', ['baseline', 'summary', 'geometry', 'partial_rotation', 'indices', 'informativeness'])
def test_snapshot_reconstruction_rejects_rehashed_false_raw_claims(monkeypatch, tamper):
    case = selected_owner(monkeypatch)
    deliver(case); legacy.step(case.owner); case.owner.inputs(TransitionInputs())
    snapshot = deepcopy(case.owner.candidate.snapshot)
    if tamper == 'baseline':
        for observation in snapshot.observations:
            observation.raw_cost = 3.
    elif tamper == 'summary':
        snapshot.candidate_cost_lower -= .1
    elif tamper == 'geometry':
        snapshot.observations[len(snapshot.observations)//2].base_x_m = 2.
    elif tamper == 'partial_rotation':
        set_time(snapshot.revolution_end[0], time_to_ns(snapshot.revolution_end[0])-100_000_000)
    elif tamper == 'indices':
        snapshot.revolution_sample_end[0] -= 1
    else:
        snapshot.informative = True
    assert not snapshot_raw_evidence(snapshot, evidence_policy='recurrent_trapping_v1').ready


def test_exact_noninitial_cycle_bounds_roundtrip(monkeypatch):
    case = selected_owner(monkeypatch, raw=None, stream_start=48.01, stream_end=60.05)
    deliver(case); legacy.step(case.owner); case.owner.inputs(TransitionInputs())
    snapshot = case.owner.candidate.snapshot
    assert snapshot is not None
    assert snapshot_raw_evidence(snapshot, evidence_policy='recurrent_trapping_v1').ready
