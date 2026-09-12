"""New typed proofs preserve old CDR schemas, hashes and clone arithmetic."""
from copy import deepcopy
import hashlib
import inspect
from pathlib import Path

import pytest
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import CandidateSnapshot, FillCommand, RecurrentCandidateSnapshot, RecurrentFillCommand
from ros_esc import v2_lifecycle as protocol
from ros_esc.v2_stream import set_time
from test_r21_trapping_fill import wrapper


def snapshot_wrapper(command_wrapper):
    msg = RecurrentCandidateSnapshot(schema_version=1, policy_id=protocol.RECURRENT_TRAPPING_POLICY)
    msg.snapshot = deepcopy(command_wrapper.command.snapshot)
    msg.confirmation, msg.diagnostic = deepcopy(command_wrapper.confirmation), deepcopy(command_wrapper.diagnostic)
    return msg


@pytest.mark.parametrize('command', [False, True])
def test_new_typed_roundtrip_preserves_original_proof_and_detached_old_payload(command):
    source = wrapper()
    original = source if command else snapshot_wrapper(source)
    kind = RecurrentFillCommand if command else RecurrentCandidateSnapshot
    clone = protocol.clone_recurrent_command if command else protocol.clone_recurrent_snapshot
    detached = clone(original)
    restored = deserialize_message(serialize_message(detached), kind)
    assert protocol.message_payload(restored) == protocol.message_payload(original)
    assert protocol.recurrent_proof_payload(restored) == protocol.recurrent_proof_payload(original)
    snap = restored.command.snapshot if command else restored.snapshot
    assert protocol.recurrent_snapshot_sha256(snap, restored) == snap.evidence_sha256
    assert protocol.snapshot_sha256(snap) != snap.evidence_sha256
    original.diagnostic.arc_radius_m[0] = .4
    original.confirmation.center_x_m = 99.
    nested = original.command.snapshot if command else original.snapshot
    nested.observations[0].raw_cost = -99.
    assert restored.diagnostic.arc_radius_m[0] == .25
    assert restored.confirmation.center_x_m == 0. and snap.observations[0].raw_cost == -1.


@pytest.mark.parametrize('field', ['policy', 'schema', 'confirmation', 'diagnostic', 'raw', 'filter_stamp'])
def test_certificate_and_snapshot_content_are_bound(field):
    msg = wrapper(); before = msg.command.evidence_sha256
    if field == 'policy': msg.policy_id = 'unknown'
    elif field == 'schema': msg.schema_version = 2
    elif field == 'confirmation': msg.confirmation.reason = 'changed original receipt'
    elif field == 'diagnostic': msg.diagnostic.reset_reason = 'changed original receipt'
    elif field == 'raw': msg.command.snapshot.observations[0].raw_cost -= .001
    elif field == 'filter_stamp': msg.command.snapshot.observation_filter_stamp[0].nanosec += 1
    if field in ('policy', 'schema'):
        with pytest.raises(ValueError): protocol.recurrent_snapshot_sha256(msg.command.snapshot, msg)
    else:
        assert protocol.recurrent_snapshot_sha256(msg.command.snapshot, msg) != before


def test_hash_ignores_only_existing_snapshot_transport_and_self_hash_fields():
    msg = wrapper(); before = protocol.recurrent_snapshot_sha256(msg.command.snapshot, msg)
    msg.command.snapshot.evidence_sha256 = 'a'*64
    set_time(msg.command.snapshot.stamp, 70_200_000_000)
    set_time(msg.command.snapshot.observations[0].stamp, 70_200_000_000)
    assert protocol.recurrent_snapshot_sha256(msg.command.snapshot, msg) == before
    set_time(msg.confirmation.stamp, 60_200_000_000)
    assert protocol.recurrent_snapshot_sha256(msg.command.snapshot, msg) != before


def test_legacy_idl_and_all_preceding_owners_are_exactly_preserved():
    prefix = inspect.getsource(protocol).split('\n\n# R21 uses separate wrapper types.', 1)[0]
    assert hashlib.sha256(prefix.encode()).hexdigest() == '79658a9203c330cb7de417195549ecb87b8a723a1f656cb27def7ef5cc1008ab'
    interfaces = Path(__file__).resolve().parents[2]/'ros_esc_interfaces'/'msg'
    for name, digest in (
        ('CandidateSnapshot.msg', 'ba61e8204e9bca08fdede48183e87ee70734aac3797820cbca449e8503401a48'),
        ('FillCommand.msg', '0799d9a62f25fa2591feacecf3d06adcbe73c2501a4a3513f6d077262f2c7480')):
        assert hashlib.sha256((interfaces/name).read_bytes()).hexdigest() == digest
    msg = wrapper().command
    for item, kind in ((msg, FillCommand), (msg.snapshot, CandidateSnapshot)):
        copied = protocol.clone_ros_message(item)
        decoded = deserialize_message(serialize_message(copied), kind)
        assert protocol.message_payload(decoded) == protocol.message_payload(item)
    assert protocol.copy_envelope(FillCommand(), msg).run_id == msg.run_id


def selected_arguments():
    return dict(simulation=True, continuous_search_mode='rolling_gesc_v2',
        metric_mode='recurrent_geometry_v3', motion_mode='centered_tracking_v1',
        algorithm_profile='robust_gaussian_v1')


@pytest.mark.parametrize('key,bad', [('simulation', False), ('simulation', 1),
    ('continuous_search_mode', 'stationary_v1'), ('metric_mode', 'pde_mean_v1'),
    ('motion_mode', 'rolling_neighborhood_v1'), ('algorithm_profile', 'legacy')])
def test_exact_selected_startup_contract_and_unchanged_default(key, bad):
    args = selected_arguments(); args[key] = bad
    with pytest.raises(ValueError):
        protocol.validate_verification_evidence_policy(protocol.RECURRENT_TRAPPING_POLICY, **args)
    assert protocol.validate_verification_evidence_policy(protocol.ANGULAR_PROFILES_POLICY, **args) == protocol.ANGULAR_PROFILES_POLICY


def test_policy_is_explicit_and_unknown_names_fail_closed():
    assert protocol.validate_verification_evidence_policy(protocol.RECURRENT_TRAPPING_POLICY, **selected_arguments()) == protocol.RECURRENT_TRAPPING_POLICY
    with pytest.raises(ValueError):
        protocol.validate_verification_evidence_policy('recurrent', **selected_arguments())
    with pytest.raises(TypeError): protocol.clone_recurrent_command(wrapper().command)
