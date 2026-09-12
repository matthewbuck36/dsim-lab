"""Ownership regressions for the existing moving snapshot and fill owners.

All inputs are generated synthetic ROS messages. Pure clone/hash parity is also
independently checked in test_q2_snapshot_clone_contract.py. No timing job, DDS,
model or retained experimental input is evaluated here.
"""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from ros_esc.v2_lifecycle import clone_ros_message, message_payload, snapshot_sha256
from ros_esc.supervisor_node import v2_supervisor
from ros_esc_interfaces.msg import CandidateSnapshot, FillCommand, SynchronizedObservation
from test_v2_supervisor import adapter, design
from test_v2_fill_transactions import owner as fill_owner, command as fill_command


class PublicationArguments:
    """Observe the exact publication argument; do not hide aliases by copying."""
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


def prepared_supervisor(monkeypatch):
    # These owner tests control ROS time explicitly. DDS tests retain the real
    # original steady clock and are run separately under their finite bounds.
    monkeypatch.setattr(v2_supervisor.time, 'monotonic_ns', lambda: 1_000_000_000)
    node, supervisor = adapter()
    supervisor.snapshot_publisher = PublicationArguments()
    supervisor.command_publisher = PublicationArguments()
    preparation = design(supervisor)
    return node, supervisor, preparation


def test_supervisor_assembly_detaches_every_observation_before_retention(monkeypatch):
    _, supervisor, preparation = prepared_supervisor(monkeypatch)
    candidate = supervisor.candidate.snapshot
    published = supervisor.snapshot_publisher.messages[0]
    template = preparation.command.snapshot
    sent = supervisor.command_publisher.messages[0].snapshot
    retained = [candidate, published, template, sent]
    assert len({id(value) for value in retained}) == 4
    hashes = [snapshot_sha256(value) for value in retained]
    assert len(set(hashes)) == 1
    original = supervisor.candidate.evidence.records[0].observation
    for value in retained:
        assert value.observations[0] is not original
        assert value.observations[0].source_stamp is not original.source_stamp
    original.raw_cost = -888.
    original.source_stamp.nanosec += 1
    original.frame_id = 'changed source'
    assert [snapshot_sha256(value) for value in retained] == hashes


@pytest.mark.parametrize('changed', ['candidate', 'publication', 'template', 'sent'])
def test_supervisor_candidate_publication_and_command_support_do_not_alias(monkeypatch, changed):
    _, supervisor, preparation = prepared_supervisor(monkeypatch)
    copies = dict(candidate=supervisor.candidate.snapshot,
                  publication=supervisor.snapshot_publisher.messages[0],
                  template=preparation.command.snapshot,
                  sent=supervisor.command_publisher.messages[0].snapshot)
    before = {name: snapshot_sha256(value) for name, value in copies.items()}
    modified = copies[changed]
    modified.observations[0].raw_cost -= .125
    modified.observations[0].source_stamp.nanosec += 1
    modified.observation_filter_state[0] = 2
    modified.revolution_start[0].nanosec += 1
    modified.observation_filter_stamp[0].nanosec += 1
    modified.observations.append(SynchronizedObservation())
    for name, value in copies.items():
        assert (snapshot_sha256(value) == before[name]) == (name != changed)


def test_later_supervisor_command_cannot_mutate_a_retained_sent_command(monkeypatch):
    _, supervisor, preparation = prepared_supervisor(monkeypatch)
    first = supervisor.command_publisher.messages[0]
    before = message_payload(first)
    supervisor._send(preparation, FillCommand.CANCEL, 'test cancellation')
    second = supervisor.command_publisher.messages[-1]
    assert first is preparation.sequences[first.command_sequence]
    assert second is preparation.sequences[second.command_sequence]
    assert first is not second and first.snapshot is not second.snapshot
    assert second.operation == FillCommand.CANCEL
    second.snapshot.observations[0].raw_cost -= .25
    second.snapshot.observation_filter_stamp[0].nanosec += 1
    second.expires_at.nanosec += 1
    assert message_payload(first) == before
    assert first.snapshot.evidence_sha256 == preparation.command.evidence_sha256


def test_gaussian_pending_command_is_detached_with_original_deadline_and_worker_support():
    node, worker, runtime = fill_owner()
    incoming = fill_command()
    before = message_payload(incoming)
    runtime.command_cb(incoming)
    assert runtime.current is not None
    pending = runtime.current
    assert pending.command is not incoming
    assert message_payload(pending.command) == before
    assert pending.wall_expires_ns == 5_000_000_000
    worker_raw = worker.input.samples[0].raw_cost
    incoming.snapshot.observations[0].raw_cost = -999.
    incoming.snapshot.observations[0].source_stamp.nanosec += 1
    incoming.snapshot.observation_filter_state[0] = 8
    incoming.snapshot.observation_filter_stamp[0].nanosec += 1
    incoming.expires_at.sec += 1
    assert message_payload(pending.command) == before
    assert worker.input.samples[0].raw_cost == worker_raw
    assert node.fill_registry.generation == 0 and not node.mirrors
    # Mutating the detached pending representation cannot reach the caller either.
    caller_after = message_payload(incoming)
    pending.command.snapshot.observations[-1].frame_id = 'pending mutation'
    assert message_payload(incoming) == caller_after


def test_clone_rejects_python_duck_types_without_calling_the_ros_serializer(monkeypatch):
    import rclpy.serialization
    monkeypatch.setattr(rclpy.serialization, 'serialize_message',
                        lambda value: pytest.fail('unsupported input reached native serializer'))
    for value in (None, {}, [], SimpleNamespace(snapshot=CandidateSnapshot())):
        with pytest.raises(TypeError):
            clone_ros_message(value)


def test_nul_guard_covers_every_string_declared_by_the_three_selected_schemas(monkeypatch):
    import rclpy.serialization
    monkeypatch.setattr(rclpy.serialization, 'serialize_message',
                        lambda value: pytest.fail('NUL-bearing input reached native serializer'))
    base = FillCommand(snapshot=CandidateSnapshot(observations=[SynchronizedObservation()]))
    for route in ((), ('snapshot',), ('snapshot', 'observations', 0)):
        original = base
        for step in route:
            original = original[step] if isinstance(step, int) else getattr(original, step)
        for name, kind in original.get_fields_and_field_types().items():
            if kind != 'string':
                continue
            message = deepcopy(base)
            target = message
            for step in route:
                target = target[step] if isinstance(step, int) else getattr(target, step)
            setattr(target, name, 'ordinary\x00truncated')
            with pytest.raises(ValueError, match='NUL'):
                clone_ros_message(message)
