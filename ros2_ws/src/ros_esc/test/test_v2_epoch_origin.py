"""Malformed Timekeeper conversion must invalidate, never escape or relatch."""

from types import SimpleNamespace

import pytest
from ros_esc.v2_epoch import EpochBinding
from ros_esc.v2_stream import relative_stamp_ns, stream_contract_id
from ros_esc_interfaces.msg import Timekeeper
from test_v2_epoch_binding import Host, arm, context


@pytest.mark.parametrize('value', [
    1e308, 2_147_483_648., -1., -1e-12,
    float('nan'), float('inf'), -float('inf'), True, None, '1.0', [],
])
def test_invalid_origin_conversion_revokes_ready_context_without_replacing_latch(value):
    node, resets = Host(), []
    binding = EpochBinding(node, resets.append)
    arm(binding, node)
    assert binding.ready()
    original = binding.origin_ns, binding.contract_id
    # SimpleNamespace also exercises malformed direct callback input that a
    # generated Timekeeper setter would itself reject; no network is involved.
    binding.set_timekeeper(SimpleNamespace(mode='sim time',start_time=value))
    assert binding.origin_fault and binding.context is None and not binding.ready()
    assert resets[-1] == 'invalid_time_origin'
    assert (binding.origin_ns,binding.contract_id) == original
    binding.set_timekeeper(Timekeeper(mode='sim time',start_time=0.))
    binding.receive_context(context(node,sequence=2))
    assert binding.origin_fault and not binding.ready()
    assert (binding.origin_ns,binding.contract_id) == original


@pytest.mark.parametrize('message', [
    SimpleNamespace(mode='sim time'), SimpleNamespace(start_time=0.),
    SimpleNamespace(mode='wall time',start_time=0.),
])
def test_missing_or_wrong_origin_fields_fail_closed(message):
    node, resets = Host(), []
    binding = EpochBinding(node,resets.append)
    binding.set_timekeeper(message)
    assert binding.origin_fault and binding.origin_ns is None and binding.contract_id is None
    assert resets == ['invalid_time_origin']


def test_invalid_first_origin_cannot_be_rehabilitated_by_later_valid_packet():
    binding = EpochBinding(Host(),lambda reason: None)
    binding.set_timekeeper(Timekeeper(mode='sim time',start_time=1e308))
    binding.set_timekeeper(Timekeeper(mode='sim time',start_time=0.))
    assert binding.origin_fault and binding.origin_ns is None and binding.contract_id is None


@pytest.mark.parametrize('value', [0., 1., 1.23456789, 2_147_483_647.5])
def test_valid_origin_preserves_existing_nanosecond_rounding_and_is_idempotent(value):
    node, resets = Host(), []
    binding = EpochBinding(node,resets.append)
    keeper = Timekeeper(mode='sim time',start_time=value)
    binding.set_timekeeper(keeper)
    expected=relative_stamp_ns(0,value)
    assert not binding.origin_fault and binding.origin_ns == expected
    assert binding.contract_id == stream_contract_id(node.config,expected)
    binding.set_timekeeper(keeper)
    assert binding.origin_ns == expected and not resets


def test_changed_finite_origin_preserves_first_latch_and_requires_new_owner():
    node, resets = Host(), []
    binding = EpochBinding(node,resets.append)
    arm(binding,node)
    original=binding.contract_id
    binding.set_timekeeper(Timekeeper(mode='sim time',start_time=.1))
    assert binding.origin_ns == 0 and binding.contract_id == original
    assert binding.origin_fault and binding.context is None and resets[-1] == 'changed_time_origin'
    binding.set_timekeeper(Timekeeper(mode='sim time',start_time=0.))
    assert binding.origin_fault and binding.contract_id == original
