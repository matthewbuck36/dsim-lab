"""Independent retirement gates: discard old valid fragments, reject corruption."""

from copy import deepcopy
from dataclasses import replace
from itertools import permutations
import math

import pytest

from ros_esc.filter_node.rolling_gesc import (
    AugmentedCost, EncoderSample, ObjectiveIdentity, PoseSample, Provenance,
    RawCost, SourceSynchronizer, StreamIdentity,
)
import test_v2_runtime as runtime


NS = 1_000_000_000
IDENTITY = StreamIdentity("expiry-independent", "contract", "odom", 0,
                          cost_key_basis="model_input_time")


def retired_core():
    core = SourceSynchronizer()
    core.set_context(IDENTITY)
    assert not core.add_raw_cost(RawCost(1., (-1.,), NS), NS).faults
    core.add_pose(PoseSample(1_400_000_000, (0., 0.), 0., 1_400_000_000, "odom"),
                  1_400_000_000)
    core.add_encoder(EncoderSample(1_400_000_000, .4, 1_400_000_000), 1_400_000_000)
    batch = core.poll(1_600_000_000)
    assert [fault.reason for fault in batch.faults] == ["pending_expired"]
    assert core.is_retired(1.) and not batch.observations
    assert core._poses and core._encoders
    return core


@pytest.mark.parametrize("corruption", [
    "raw_nan", "raw_empty", "augmented_nan", "augmented_bad_objective",
    "wrong_run", "wrong_frame", "wrong_origin", "wrong_source_key",
    "invalid_geometry", "invalid_receipt", "future_receipt",
])
def test_retired_core_key_does_not_mask_structural_or_identity_fault(corruption):
    core = retired_core()
    now = 2*NS  # Benign age alone would no longer be a new fault.
    operation = core.add_raw_cost
    sample = RawCost(1., (-1.,), now)
    if corruption == "raw_nan":
        sample = replace(sample, values=(math.nan,))
    elif corruption == "raw_empty":
        sample = replace(sample, values=())
    elif corruption == "invalid_receipt":
        sample = replace(sample, receipt_ns=-1)
    elif corruption == "future_receipt":
        sample = replace(sample, receipt_ns=now+1)
    elif corruption.startswith("augmented"):
        operation = core.add_augmented
        sample = AugmentedCost(1., (math.nan if corruption.endswith("nan") else -1.,),
                               ObjectiveIdentity(-1 if corruption.endswith("objective") else 1), now)
    else:
        operation = core.add_provenance
        sample = Provenance(1., 1, NS, NS, (.18, 0.), .4, IDENTITY, now)
        if corruption == "wrong_run":
            sample = replace(sample, identity=replace(IDENTITY, run_id="other"))
        elif corruption == "wrong_frame":
            sample = replace(sample, identity=replace(IDENTITY, frame_id="map"))
        elif corruption == "wrong_origin":
            sample = replace(sample, identity=replace(IDENTITY, time_origin_ns=1))
        elif corruption == "wrong_source_key":
            sample = replace(sample, model_input_ns=NS+1_000_000)
        else:
            sample = replace(sample, sensor_xy=(math.nan, 0.))
    batch = operation(sample, now)
    assert batch.faults and not batch.observations
    assert not core._poses and not core._encoders


@pytest.fixture
def retired_adapter(monkeypatch):
    monkeypatch.setattr(runtime, "CONFIG", dict(runtime.CONFIG, schema_version=2,
                                               cost_key_basis="model_input_time"))
    node, adapter = runtime.make_filter()
    rows = runtime.messages(NS)
    for name in ("raw", "augmented"):
        rows[name].timestamp = 1.
    for name in ("provenance", "objective"):
        rows[name].schema_version = 2
        rows[name].legacy_cost_source_timestamp_sec = 1.
    node.now_ns = NS
    adapter.add_raw(rows["raw"])
    runtime.support(node, adapter, 1_400_000_000)
    node.now_ns = 1_600_000_000
    adapter.poll()
    assert adapter.sync.is_retired(1.)
    assert adapter.sync._poses and adapter.sync._encoders
    return node, adapter, rows


@pytest.mark.parametrize("order", tuple(permutations(("raw", "augmented", "provenance", "objective"))))
def test_retired_valid_packets_are_inert_in_every_cost_arrival_order(retired_adapter, order):
    node, adapter, rows = retired_adapter
    initial = (adapter.sync.reset_sequence, adapter.rolling.reset_sequence)
    pose_receipts = [(p.stamp_ns, p.receipt_ns) for p in adapter.sync._poses]
    encoder_receipts = [(p.stamp_ns, p.receipt_ns) for p in adapter.sync._encoders]
    for now in (2*NS, 3*NS):
        node.now_ns = now
        for name in order:
            getattr(adapter, "add_"+name)(rows[name])
        adapter.poll()
        assert (adapter.sync.reset_sequence, adapter.rolling.reset_sequence) == initial
        assert not adapter.pending and not adapter.sync._pending
        assert not node.filter_publisher.messages
        assert [(p.stamp_ns, p.receipt_ns) for p in adapter.sync._poses] == pose_receipts
        assert [(p.stamp_ns, p.receipt_ns) for p in adapter.sync._encoders] == encoder_receipts
        assert not adapter._output_result(now).output_valid


@pytest.mark.parametrize("kind,corruption", [
    ("raw", "nan"), ("raw", "empty"), ("augmented", "nan"),
    ("augmented", "empty"), ("provenance", "identity"),
    ("provenance", "geometry"), ("objective", "geometry"),
    ("objective", "arithmetic"), ("objective", "hash"),
])
def test_retired_wire_payload_corruption_keeps_hard_invalidation(retired_adapter, kind, corruption):
    node, adapter, rows = retired_adapter
    node.now_ns = 2*NS
    message = deepcopy(rows[kind])
    if kind in ("raw", "augmented"):
        message.data = [math.nan] if corruption == "nan" else []
    elif corruption == "identity":
        message.run_id = "foreign-run"
    elif corruption == "geometry":
        message.sensor_x_m = [math.nan]
    elif corruption == "arithmetic":
        message.augmented_cost = [999.]
    else:
        message.objective_sha256 = "0"*64
    before = adapter.sync.reset_sequence
    getattr(adapter, "add_"+kind)(message)
    assert adapter.sync.reset_sequence > before
    assert not adapter.sync._poses and not adapter.sync._encoders
    assert not node.filter_publisher.messages


def test_explicit_source_revocation_overrides_retirement_and_is_idempotent(retired_adapter):
    node, adapter, rows = retired_adapter
    node.now_ns = 2*NS
    notice = deepcopy(rows["provenance"])
    notice.source_sequence += 1  # A notice consumes the source owner's next sequence.
    notice.sensor_transform_valid = False
    adapter.add_provenance(notice)
    reset = adapter.sync.reset_sequence
    assert adapter.completed[1.]["poisoned"]
    assert not adapter.sync._poses and not adapter.sync._encoders
    adapter.add_provenance(notice)
    assert adapter.sync.reset_sequence == reset
    for name, message in rows.items():
        getattr(adapter, "add_"+name)(message)
    assert not adapter.pending and not node.filter_publisher.messages
    assert adapter.completed[1.]["poisoned"]


def test_retirement_does_not_hide_clock_rollback_or_replace_context():
    core = retired_core()
    assert core.add_raw_cost(RawCost(1., (-1.,), 1_500_000_000), 1_500_000_000).faults
    assert not core._poses and not core._encoders
    replacement = replace(IDENTITY, run_id="next-run", stream_contract_id="next-contract")
    assert core.set_context(replacement).faults
    assert not core.is_retired(1.)
    assert not core.add_raw_cost(RawCost(1., (-1.,), NS), NS).faults
    assert 1. in core._pending
