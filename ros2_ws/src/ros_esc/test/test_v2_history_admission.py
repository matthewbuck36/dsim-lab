"""Arm C publication-clock admission with immutable first receipts and revocations."""

from copy import deepcopy

import pytest

from ros_esc.convergence_detector_node import v2_binding as module
from ros_esc.convergence_detector_node.v2_binding import V2DetectorBinding
from ros_esc.pde_history_node.v2_evidence import history_sha256
from ros_esc.v2_stream import set_time, time_to_ns
from test_v2_epoch_binding import Host, arm, context, legacy_payload, pde_host, pose


NS = 1_000_000_000


def host(monkeypatch):
    node = Host()
    node.steady_ns = NS
    monkeypatch.setattr(module.time, 'monotonic_ns', lambda: node.steady_ns)
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node)
    return node, adapter


def actual_wrappers():
    pde = pde_host()
    owner = pde.v2_evidence
    owner.receive_pose(pose())
    first = deepcopy(owner.publisher.messages[-1])
    pde.now_ns = NS + 100_000_000
    owner.receive_pose(pose(pde.now_ns))
    second = deepcopy(owner.publisher.messages[-1])
    owner.receive_pose(pose(pde.now_ns, x=99.))
    revoked = deepcopy(owner.publisher.messages[-1])
    pde.now_ns = NS + 200_000_000
    owner.receive_pose(pose(pde.now_ns))
    recovered = deepcopy(owner.publisher.messages[-1])
    return first, second, revoked, recovered


def test_future_pde_publication_waits_for_clock_and_keeps_original_receipt(monkeypatch):
    node, adapter = host(monkeypatch)
    future = actual_wrappers()[1]
    expected = list(future.history.data)
    adapter.receive_history(future)
    future.history.data[0] = 999.
    assert adapter.history is None and not node.buffers and len(adapter.history_pending) == 1
    node.now_ns = NS + 99_999_999
    adapter.poll_history()
    assert not node.buffers
    node.now_ns += 1
    adapter.poll_history()
    assert len(node.buffers) == 1 and list(node.buffers[0].data) == expected
    assert adapter.latest_history_receipt == (NS,NS)
    assert time_to_ns(adapter.history.stamp) == node.now_ns
    assert adapter.last_history_sequence == 2


@pytest.mark.parametrize('future', [False, True])
def test_duplicate_history_cannot_refresh_paused_clock_receipts(monkeypatch, future):
    node, adapter = host(monkeypatch)
    wire = actual_wrappers()[int(future)]
    adapter.receive_history(wire)
    node.steady_ns += 400_000_000
    adapter.receive_history(deepcopy(wire))
    node.steady_ns += 100_000_001
    adapter.poll_history()
    assert adapter.history is None and not adapter.history_pending
    node.now_ns = NS + 100_000_000
    adapter.receive_history(wire)
    assert adapter.history is None
    assert len(node.buffers) == int(not future)


def test_future_revocation_fences_old_support_and_preserves_later_pending_recovery(monkeypatch):
    node, adapter = host(monkeypatch)
    first, second, revoked, recovered = actual_wrappers()
    adapter.receive_history(first)
    adapter.receive_history(second)
    adapter.receive_history(revoked)
    assert adapter.history is None and adapter.last_history_sequence == 1
    assert adapter.history_frontier == 3 and len(adapter.history_pending) == 1
    adapter.receive_history(second)  # Old identical pending support cannot return.
    adapter.receive_history(recovered)
    assert len(adapter.history_pending) == 2
    node.now_ns = NS + 100_000_000
    adapter.poll_history()
    assert adapter.history is None and adapter.last_history_sequence == 3
    assert len(adapter.history_pending) == 1
    node.now_ns += 100_000_000
    adapter.poll_history()
    assert adapter.history.history_sequence == 4 and len(node.buffers) == 2
    assert time_to_ns(adapter.history.input_start) == node.now_ns


def test_unseen_pre_revocation_packet_cannot_revive_after_clock_catches_up(monkeypatch):
    node, adapter = host(monkeypatch)
    first, second, revoked, recovered = actual_wrappers()
    adapter.receive_history(first)
    adapter.receive_history(revoked)
    adapter.receive_history(second)
    node.now_ns = NS + 100_000_000
    adapter.poll_history()
    assert adapter.history is None and len(node.buffers) == 1
    node.now_ns += 100_000_000
    adapter.receive_history(recovered)
    assert adapter.history.history_sequence == 4


def test_conflicting_pending_sequence_is_tombstoned_until_newer_input(monkeypatch):
    node, adapter = host(monkeypatch)
    _, second, _, recovered = actual_wrappers()
    adapter.receive_history(second)
    conflicting = deepcopy(second)
    conflicting.history.data[0] = 500.
    conflicting.history_sha256 = history_sha256(conflicting)
    adapter.receive_history(conflicting)
    assert not adapter.history_pending and adapter.history_seen[2] is None
    node.now_ns = NS + 100_000_000
    adapter.receive_history(second)
    assert not node.buffers
    node.now_ns += 100_000_000
    adapter.receive_history(recovered)
    assert adapter.history.history_sequence == 4


@pytest.mark.parametrize('change', ['hash', 'run', 'origin', 'epoch', 'frame', 'invalid_revocation', 'far_future'])
def test_unqualified_envelope_never_enters_queue_or_advances_frontier(monkeypatch, change):
    node, adapter = host(monkeypatch)
    wire = deepcopy(actual_wrappers()[1])
    if change == 'hash': wire.history.data[0] = 9.
    elif change == 'run': wire.run_id = 'other'
    elif change == 'origin': set_time(wire.time_origin,1)
    elif change == 'epoch': wire.search_epoch += 1
    elif change == 'frame': wire.frame_id = 'map'
    elif change == 'invalid_revocation': wire.valid = False
    elif change == 'far_future':
        future = NS+500_000_001
        for field in ('stamp','input_end','latest_input_receipt'): set_time(getattr(wire,field),future)
        wire.history.timestamp = future/NS
    if change != 'hash': wire.history_sha256 = history_sha256(wire)
    adapter.receive_history(wire)
    assert not adapter.history_pending and adapter.history_frontier == 0
    assert not adapter.history_seen and not node.buffers


def test_new_context_sequence_can_arrive_after_queued_history(monkeypatch):
    node, adapter = host(monkeypatch)
    wire = actual_wrappers()[1]
    wire.context_sequence = 2
    wire.history_sha256 = history_sha256(wire)
    adapter.receive_history(wire)
    node.now_ns = NS+100_000_000
    adapter.poll_history()
    assert not node.buffers
    adapter.binding.receive_context(context(node,sequence=2))
    adapter.poll_history()
    assert len(node.buffers) == 1


def test_epoch_exit_discards_pending_history_and_retry_cannot_rebind_it(monkeypatch):
    node, adapter = host(monkeypatch)
    future = actual_wrappers()[1]
    adapter.receive_history(future)
    node.now_ns = NS+100_000_000
    adapter.binding.receive_context(context(node,sequence=2,state=2))
    assert not adapter.history_pending
    adapter.binding.receive_context(context(node,sequence=3,epoch=2,start=node.now_ns))
    adapter.receive_history(future)
    assert not node.buffers and adapter.history is None


def test_history_queue_capacity_rejects_without_forgetting_sequence_fence(monkeypatch):
    assert module.MAX_PENDING_HISTORIES == 1024
    monkeypatch.setattr(module,'MAX_PENDING_HISTORIES',3)
    node, adapter = host(monkeypatch)
    base = actual_wrappers()[1]
    for sequence in range(1,5):
        wire = deepcopy(base); wire.history_sequence = sequence
        wire.history_sha256 = history_sha256(wire)
        adapter.receive_history(wire)
    assert not adapter.history_pending and adapter.history_frontier == 4
    assert not node.buffers
    node.now_ns = NS+100_000_000
    original = deepcopy(base); original.history_sequence = 1; original.history_sha256 = history_sha256(original)
    adapter.receive_history(original)
    assert not node.buffers


def test_final_legacy_publication_rechecks_first_receiver_receipt(monkeypatch):
    node, adapter = host(monkeypatch)
    adapter.receive_history(actual_wrappers()[0])
    node.steady_ns += 500_000_001  # Simulated processing delay while /clock stays held.
    assert not adapter.publish_legacy(legacy_payload())
    assert not adapter.publisher.messages and adapter.history is None


def test_expired_sender_support_is_not_rehabilitated_by_fresh_receiver_admission(monkeypatch):
    node, adapter = host(monkeypatch)
    wire = actual_wrappers()[1]
    set_time(wire.input_end, 600_000_000)  # More than0.5s before publisher clock.
    wire.history_sha256 = history_sha256(wire)
    adapter.receive_history(wire)
    assert not node.buffers and not adapter.history_pending


def test_original_receipts_can_precede_nonzero_origin_during_clock_admission(monkeypatch):
    from ros_esc_interfaces.msg import Timekeeper
    from ros_esc.v2_stream import stream_contract_id
    node = Host(); node.now_ns = 9_900_000_000; node.steady_ns = NS
    monkeypatch.setattr(module.time,'monotonic_ns',lambda: node.steady_ns)
    adapter = V2DetectorBinding(node)
    origin = 10*NS
    adapter.binding.set_timekeeper(Timekeeper(mode='sim time',start_time=10.))
    ctx = context(node,start=origin)
    set_time(ctx.stamp,origin); set_time(ctx.time_origin,origin)
    ctx.stream_contract_id = stream_contract_id(node.config,origin)
    adapter.binding.receive_context(ctx)
    wire = actual_wrappers()[0]
    wire.stream_contract_id = ctx.stream_contract_id
    for field in ('time_origin','epoch_started_at','input_start','input_end','stamp'):
        set_time(getattr(wire,field),origin)
    set_time(wire.latest_input_receipt,node.now_ns)
    wire.history.timestamp = 10.
    wire.history_sha256 = history_sha256(wire)
    adapter.receive_history(wire)
    assert len(adapter.history_pending) == 1 and not node.buffers
    node.now_ns = origin
    adapter.poll_history()
    assert len(node.buffers) == 1
    assert time_to_ns(adapter.history.latest_input_receipt) == 9_900_000_000
    assert adapter.latest_history_receipt[0] == 9_900_000_000
