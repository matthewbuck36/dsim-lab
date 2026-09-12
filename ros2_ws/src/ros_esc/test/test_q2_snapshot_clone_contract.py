"""Independent generated-wire clone checks against the immutable D3 hash owner.

Only synthetic support is constructed here. The archive is read for one source
module; no historical observations, bags, reference values or timing runs enter
these checks. CDR alignment bytes are not message fields: the first retained
test run exposed nondeterministic padding. Every declared float leaf is instead
compared bit-for-bit, including after serialization/deserialization.
"""

import array
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import tarfile

import pytest
from builtin_interfaces.msg import Time
from rclpy.serialization import deserialize_message, serialize_message
from ros_esc_interfaces.msg import CandidateSnapshot, FillCommand, SynchronizedObservation

from ros_esc.v2_lifecycle import clone_ros_message, message_payload, snapshot_sha256
from ros_esc.v2_stream import canonical_json, set_time


CHECKPOINT = Path('/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/'
                  'q1_direction_policy_closed_v1')
MANIFEST_SHA = '995d9547ef5ce1096e012c9e4741c193e675c02ae29f3dfa1c2e42b2d8603fbf'
ARCHIVE_SHA = 'c36993ddaaab3822859bd869135bad06bb512d7eb44ad475484d778ff8fd7237'
ORACLE_MEMBER = 'ros2_ws/src/ros_esc/ros_esc/v2_lifecycle.py'
ORACLE_SHA = '8fb8c42e5c1173f5955e28a13afee71efdf5fa5270af07feda566c0771d96492'


@pytest.fixture(scope='module')
def old_hash_owner(tmp_path_factory):
    manifest_bytes = (CHECKPOINT / 'manifest.json').read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA
    manifest = json.loads(manifest_bytes)
    archive = CHECKPOINT / 'source_and_evidence.tar.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA
    assert any(item['path'] == str(archive) and item['sha256'] == ARCHIVE_SHA
               for item in manifest['artifacts'])
    assert any(item['path'] == ORACLE_MEMBER and item['sha256'] == ORACLE_SHA
               for item in manifest['files'])
    with tarfile.open(archive, 'r:gz') as source_archive:
        source = source_archive.extractfile(ORACLE_MEMBER).read()
    assert hashlib.sha256(source).hexdigest() == ORACLE_SHA
    oracle_path = tmp_path_factory.mktemp('d3_hash_source') / 'v2_lifecycle.py'
    oracle_path.write_bytes(source)
    spec = importlib.util.spec_from_file_location('q2_immutable_d3_hash', oracle_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _times(message, start_ns):
    for offset, name in enumerate(message.get_fields_and_field_types()):
        value = getattr(message, name)
        if type(value) is Time:
            set_time(value, start_ns + offset)


def _snapshot(count):
    assert 0 <= count <= 4000
    snapshot = CandidateSnapshot(
        schema_version=1, run_id='clone-run', stream_contract_id='a' * 64,
        frame_id='odom', search_epoch=2**53 + 7, candidate_id=2**63 + 19,
        objective_revision=7, detector_confirmation_sequence=5,
        snapshot_revision=3, metric_mode='centroid_windows_v2',
        center_x_m=-0.0, center_y_m=1.25, neighborhood_radius_m=.75,
        centroid_tolerance_m=.1, convergence_score_m=.23,
        convergence_score_valid=True, legacy_r_mean_m2=float('nan'),
        legacy_r_mean_valid=False, candidate_cost_estimate=-.1,
        candidate_cost_mad=.002, candidate_cost_uncertainty=.003,
        candidate_cost_lower=-.103, candidate_cost_upper=-.097,
        information_amplitude=.04, information_disagreement=.001,
        information_floor=1e-6, informative=True,
        completed_revolutions=3, pretrigger_revolutions=2,
        verification_revolutions=1)
    _times(snapshot, 2_000_000_000_000_000_000)
    observations = []
    for index in range(count):
        observation = SynchronizedObservation(
            schema_version=2, run_id=snapshot.run_id,
            stream_contract_id=snapshot.stream_contract_id, frame_id='odom',
            observation_id=2**53 + index + 1, source_sequence=2**63 + index + 1,
            objective_revision=7, channel_index=0,
            legacy_cost_source_timestamp_sec=index * .034,
            base_x_m=-0.0 if index % 2 else .1, base_y_m=.2,
            base_yaw_rad=.3, sensor_phase_rad=.4, encoder_phase_rad=.4,
            phase_disagreement_rad=-0.0, demodulation_phase_reconstructed=True,
            sensor_world_phase_rad=.7, sensor_x_m=.15, sensor_y_m=.25,
            raw_cost=-.01, augmented_cost=-.009, sync_error_sec=.001,
            raw_cost_valid=True, augmented_cost_valid=True,
            synchronized_valid=True, sensor_transform_observed=True)
        _times(observation, 2_000_000_000_000_000_000 + index * 34_000_000)
        observations.append(observation)
    snapshot.observations = observations
    snapshot.observation_filter_state = [1 + index % 3 for index in range(count)]
    snapshot.observation_filter_stamp = [copy.deepcopy(obs.admission_stamp)
                                         for obs in observations]
    starts = [0, count // 3, 2 * count // 3]
    ends = [count // 3, 2 * count // 3, count]
    snapshot.revolution_sample_start = starts
    snapshot.revolution_sample_end = ends
    snapshot.revolution_start = [Time(sec=20 + index, nanosec=index + 1)
                                 for index in range(3)]
    snapshot.revolution_end = [Time(sec=21 + index, nanosec=index + 2)
                               for index in range(3)]
    return snapshot


def _command(snapshot):
    command = FillCommand(
        schema_version=1, run_id=snapshot.run_id,
        stream_contract_id=snapshot.stream_contract_id, frame_id='odom',
        search_epoch=snapshot.search_epoch, candidate_id=snapshot.candidate_id,
        objective_revision=snapshot.objective_revision,
        operation=FillCommand.PREPARE, command_sequence=2**63 + 3,
        preparation_id=2**53 + 1, expected_registry_generation=7,
        target_fill_id=2**53 + 9, target_cluster_id=2**53 + 11,
        target_revision=2**32 - 1, evidence_sha256='b' * 64,
        prepared_sha256='c' * 64, reason='préparer — κέντρο 🐢',
        snapshot=snapshot, redesign=True, return_state=4)
    _times(command, 2_000_000_000_000_000_000)
    return command


def _canonical(message):
    return canonical_json(message_payload(message))


def _assert_declared_fields(expected, actual, path='message'):
    """Compare all declared values without NaN equality or padding assumptions."""
    assert type(actual) is type(expected), path
    if isinstance(expected, float):
        assert struct.pack('!d', actual) == struct.pack('!d', expected), path
    elif isinstance(expected, (str, int, bool)):
        assert actual == expected, path
    elif hasattr(expected, 'get_fields_and_field_types'):
        fields = expected.get_fields_and_field_types()
        assert fields == actual.get_fields_and_field_types(), path
        for name in fields:
            _assert_declared_fields(getattr(expected, name), getattr(actual, name),
                                    f'{path}.{name}')
    else:
        assert len(actual) == len(expected), path
        if hasattr(expected, 'typecode'):
            assert actual.typecode == expected.typecode, path
        for index, (left, right) in enumerate(zip(expected, actual)):
            _assert_declared_fields(left, right, f'{path}[{index}]')


@pytest.mark.parametrize('count', [0, 1, 363, 4000])
@pytest.mark.parametrize('wrapped', [False, True], ids=['snapshot', 'command'])
def test_full_generated_support_preserves_deepcopy_wire_and_d3_hash(
        old_hash_owner, count, wrapped):
    original_snapshot = _snapshot(count)
    original_snapshot.evidence_sha256 = old_hash_owner.snapshot_sha256(original_snapshot)
    message = _command(original_snapshot) if wrapped else original_snapshot
    before = _canonical(message)
    detached = clone_ros_message(message)
    old_copy = copy.deepcopy(message)
    cloned_snapshot = detached.snapshot if wrapped else detached
    assert type(detached) is type(message)
    assert detached is not message
    cloned_bytes, old_bytes = serialize_message(detached), serialize_message(old_copy)
    assert len(cloned_bytes) == len(old_bytes)
    assert cloned_bytes[:4] == old_bytes[:4]  # Same CDR encapsulation.
    _assert_declared_fields(old_copy, detached)
    _assert_declared_fields(message, deserialize_message(cloned_bytes, type(message)))
    _assert_declared_fields(message, deserialize_message(old_bytes, type(message)))
    assert _canonical(detached) == before == _canonical(message)
    assert snapshot_sha256(cloned_snapshot) == original_snapshot.evidence_sha256
    assert old_hash_owner.snapshot_sha256(cloned_snapshot) == original_snapshot.evidence_sha256
    assert snapshot_sha256(original_snapshot) == original_snapshot.evidence_sha256
    if count:
        assert cloned_snapshot.observations[0] is not original_snapshot.observations[0]
        assert cloned_snapshot.observations[-1] is not original_snapshot.observations[-1]


def test_both_direction_nested_mutations_do_not_cross_snapshot_command_ownership(old_hash_owner):
    source = _snapshot(4)
    command = _command(source)
    copied = clone_ros_message(command)
    original_payload = _canonical(command)
    copied.snapshot.observations[0].source_stamp.nanosec += 100
    copied.snapshot.observations[1].raw_cost = -.4
    copied.snapshot.observation_filter_state[2] = 8
    copied.snapshot.observation_filter_stamp[3].nanosec += 10
    copied.snapshot.revolution_start[1].sec += 3
    copied.snapshot.revolution_sample_start[1] = 0
    copied.expires_at.sec += 1
    copied.reason = 'local copy changed'
    assert _canonical(command) == original_payload
    detached_payload = _canonical(copied)
    source.observations[3].admission_stamp.nanosec += 1
    source.observation_filter_state[0] = 5
    source.observation_filter_stamp[0].sec += 1
    source.revolution_end[0].nanosec += 5
    source.revolution_sample_end[0] = 0
    source.observations.append(SynchronizedObservation())
    command.time_origin.sec -= 1
    assert _canonical(copied) == detached_payload
    for snapshot in (source, copied.snapshot):
        assert snapshot_sha256(snapshot) == old_hash_owner.snapshot_sha256(snapshot)


@pytest.mark.parametrize('value', [
    -0.0, 0.0, float('nan'), float('inf'), -float('inf'),
    5e-324, -5e-324, 1.7976931348623157e308,
])
def test_optional_float_values_keep_ieee_bits_beyond_canonical_null(value, old_hash_owner):
    snapshot = _snapshot(1)
    snapshot.legacy_r_mean_m2 = value
    snapshot.information_disagreement = value
    snapshot.observations[0].phase_disagreement_rad = value
    cloned = clone_ros_message(snapshot)
    for expected, actual in (
        (snapshot.legacy_r_mean_m2, cloned.legacy_r_mean_m2),
        (snapshot.information_disagreement, cloned.information_disagreement),
        (snapshot.observations[0].phase_disagreement_rad,
         cloned.observations[0].phase_disagreement_rad),
    ):
        assert struct.pack('!d', actual) == struct.pack('!d', expected)
        if math.isnan(expected):
            assert math.isnan(actual)
    assert snapshot_sha256(cloned) == old_hash_owner.snapshot_sha256(snapshot)


@pytest.mark.parametrize('location', ['command', 'snapshot', 'observation'])
def test_each_embedded_nul_rejected_before_native_conversion(location, monkeypatch):
    command = _command(_snapshot(1))
    owner, field = {
        'command': (command, 'reason'),
        'snapshot': (command.snapshot, 'metric_mode'),
        'observation': (command.snapshot.observations[0], 'frame_id'),
    }[location]
    setattr(owner, field, 'prefix\x00suffix')
    before = _canonical(command)

    def forbidden_native_call(_message):
        pytest.fail('lossy native string conversion must not run')

    monkeypatch.setattr('rclpy.serialization.serialize_message', forbidden_native_call)
    with pytest.raises(ValueError, match='NUL'):
        clone_ros_message(command)
    assert _canonical(command) == before


@pytest.mark.parametrize('location', ['command', 'snapshot', 'observation'])
def test_ordinary_unicode_survives_every_supported_string_depth(location):
    command = _command(_snapshot(1))
    owner, field = {
        'command': (command, 'reason'),
        'snapshot': (command.snapshot, 'run_id'),
        'observation': (command.snapshot.observations[0], 'run_id'),
    }[location]
    setattr(owner, field, 'ελληνικά / 日本語 / 🐢 / e\u0301')
    # Clone equivalence is distinct from a runtime identity authorization check.
    cloned = clone_ros_message(command)
    assert _canonical(cloned) == _canonical(command)
    _assert_declared_fields(command, cloned)
    _assert_declared_fields(command, deserialize_message(serialize_message(cloned), FillCommand))


@pytest.mark.parametrize('field', ['source_stamp', 'admission_stamp', 'oldest_receipt_stamp'])
def test_source_and_original_admission_time_are_still_hash_inputs(field, old_hash_owner):
    original = _snapshot(1)
    modified = clone_ros_message(original)
    getattr(modified.observations[0], field).nanosec += 1
    assert snapshot_sha256(modified) != snapshot_sha256(original)
    assert snapshot_sha256(modified) == old_hash_owner.snapshot_sha256(modified)


@pytest.mark.parametrize('field', ['objective_revision', 'source_sequence', 'observation_id'])
def test_observation_identity_remains_in_hash(field, old_hash_owner):
    original = _snapshot(1)
    modified = clone_ros_message(original)
    observation = modified.observations[0]
    setattr(observation, field, getattr(observation, field) + 1)
    assert snapshot_sha256(modified) != snapshot_sha256(original)
    assert snapshot_sha256(modified) == old_hash_owner.snapshot_sha256(modified)


def test_valid_excluded_publication_fields_remain_hash_invariant(old_hash_owner):
    snapshot = _snapshot(1)
    original = old_hash_owner.snapshot_sha256(snapshot)
    snapshot.stamp.nanosec += 10
    snapshot.observations[0].stamp.nanosec += 11
    snapshot.evidence_sha256 = 'different excluded value'
    assert snapshot_sha256(snapshot) == original
    assert old_hash_owner.snapshot_sha256(snapshot) == original


@pytest.mark.parametrize('sec,nanosec', [(-1, 0), (0, 1_000_000_000)])
def test_malformed_excluded_observation_publication_time_still_rejected(
        old_hash_owner, sec, nanosec):
    snapshot = _snapshot(1)
    snapshot.observations[0].stamp = Time(sec=sec, nanosec=nanosec)
    with pytest.raises(ValueError):
        old_hash_owner.snapshot_sha256(snapshot)
    with pytest.raises(ValueError):
        snapshot_sha256(snapshot)


@pytest.mark.parametrize('value', [None, {}, [], object(), Time(), SynchronizedObservation()])
def test_generic_objects_and_unselected_wire_types_are_not_clone_inputs(value):
    with pytest.raises(TypeError):
        clone_ros_message(value)


@pytest.mark.parametrize('kind', [CandidateSnapshot, FillCommand, SynchronizedObservation, Time])
@pytest.mark.parametrize('change', ['field_type', 'extra_slot', 'slot_types'])
def test_warmed_schema_plan_rejects_each_changed_generated_definition(kind, change, monkeypatch):
    command = _command(_snapshot(1))
    clone_ros_message(command)  # Guard must still apply after plans are cached.
    if change == 'field_type':
        fields = dict(kind.get_fields_and_field_types())
        fields[next(iter(fields))] = 'string'
        monkeypatch.setattr(kind, '_fields_and_field_types', fields)
    elif change == 'extra_slot':
        monkeypatch.setattr(kind, '__slots__', [*kind.__slots__, '_unexpected_field'])
    else:
        monkeypatch.setattr(kind, 'SLOT_TYPES', ())
    with pytest.raises(TypeError, match='schema'):
        clone_ros_message(command)


@pytest.mark.parametrize('change', ['added', 'missing'])
def test_supported_field_names_do_not_expand_or_disappear_implicitly(change, monkeypatch):
    snapshot = _snapshot(1)
    clone_ros_message(snapshot)
    fields = dict(SynchronizedObservation.get_fields_and_field_types())
    if change == 'added':
        fields['new_measurement'] = 'double'
    else:
        del fields['source_sequence']
    monkeypatch.setattr(SynchronizedObservation, '_fields_and_field_types', fields)
    with pytest.raises(TypeError, match='schema'):
        clone_ros_message(snapshot)


def _owner_at(command, location):
    return {
        'command': command,
        'snapshot': command.snapshot,
        'observation': command.snapshot.observations[0],
        'time': command.snapshot.observations[0].source_stamp,
    }[location]


@pytest.mark.parametrize('location,slot,value', [
    ('command', '_operation', True),
    ('command', '_redesign', 1),
    ('command', '_reason', b'not text'),
    ('snapshot', '_schema_version', 1.0),
    ('snapshot', '_informative', 1),
    ('snapshot', '_center_x_m', 1),
    ('snapshot', '_run_id', None),
    ('observation', '_source_sequence', True),
    ('observation', '_raw_cost', '0.01'),
    ('observation', '_raw_cost_valid', 0),
    ('time', '_sec', 1.0),
    ('time', '_nanosec', False),
])
def test_corrupt_private_primitive_types_are_rejected_before_copy(location, slot, value):
    command = _command(_snapshot(1))
    # Deliberately bypass generated setters. Calling native CDR on some such
    # corruptions can assert in C; no unsafe native-comparison oracle is used.
    setattr(_owner_at(command, location), slot, value)
    with pytest.raises(TypeError):
        clone_ros_message(command)


@pytest.mark.parametrize('location,slot,value', [
    ('command', '_operation', 256),
    ('command', '_target_revision', 2**32),
    ('snapshot', '_schema_version', -1),
    ('snapshot', '_schema_version', 2**16),
    ('observation', '_source_sequence', -1),
    ('observation', '_source_sequence', 2**64),
    ('time', '_sec', -(2**31) - 1),
    ('time', '_sec', 2**31),
    ('time', '_nanosec', -1),
    ('time', '_nanosec', 2**32),
])
def test_integer_overflow_is_rejected_instead_of_private_slot_or_c_cast_wrap(
        location, slot, value):
    command = _command(_snapshot(1))
    setattr(_owner_at(command, location), slot, value)
    with pytest.raises(ValueError):
        clone_ros_message(command)


@pytest.mark.parametrize('primitive', [int, float, str])
def test_mutable_primitive_subclass_instances_are_outside_canonical_inputs(primitive):
    class MutableScalar(primitive):
        pass

    snapshot = _snapshot(1)
    field, initial = {int: ('candidate_id', 1), float: ('center_x_m', .25),
                      str: ('run_id', 'run')}[primitive]
    value = MutableScalar(initial)
    value.mutable_state = []
    setattr(snapshot, '_' + field, value)
    with pytest.raises(TypeError):
        clone_ros_message(snapshot)


@pytest.mark.parametrize('slot,value', [
    ('_revolution_sample_start', array.array('B', [0, 1, 2])),
    ('_revolution_sample_end', array.array('Q', [1, 2, 3])),
    ('_observation_filter_state', array.array('I', [1])),
    ('_observation_filter_state', [1]),
    ('_observations', (SynchronizedObservation(),)),
    ('_revolution_start', (Time(),)),
])
def test_noncanonical_sequences_cannot_be_reinterpreted_as_typed_buffers(slot, value):
    snapshot = _snapshot(1)
    setattr(snapshot, slot, value)
    with pytest.raises(TypeError):
        clone_ros_message(snapshot)


@pytest.mark.parametrize('location,slot,value', [
    ('command', '_snapshot', Time()),
    ('snapshot', '_stamp', SynchronizedObservation()),
    ('snapshot', '_observations', [Time()]),
    ('snapshot', '_observation_filter_stamp', [SynchronizedObservation()]),
    ('observation', '_source_stamp', CandidateSnapshot()),
])
def test_wrong_nested_generated_types_fail_without_unbounded_structural_recursion(
        location, slot, value):
    command = _command(_snapshot(1))
    setattr(_owner_at(command, location), slot, value)
    with pytest.raises(TypeError):
        clone_ros_message(command)


def test_generated_message_subclasses_are_rejected_at_root_and_nested_positions():
    class SnapshotSubclass(CandidateSnapshot):
        pass

    class TimeSubclass(Time):
        pass

    with pytest.raises(TypeError):
        clone_ros_message(SnapshotSubclass())
    snapshot = _snapshot(1)
    snapshot.observations[0].source_stamp = TimeSubclass(sec=1)
    with pytest.raises(TypeError):
        clone_ros_message(snapshot)


@pytest.mark.parametrize('location', ['command', 'snapshot', 'observation'])
def test_unpaired_surrogates_fail_before_downstream_native_string_conversion(location):
    command = _command(_snapshot(1))
    field = 'reason' if location == 'command' else 'run_id'
    setattr(_owner_at(command, location), field, 'prefix\ud800suffix')
    with pytest.raises(UnicodeEncodeError):
        clone_ros_message(command)


def test_repeated_input_aliases_are_detached_per_occurrence_like_cdr():
    source = _snapshot(2)
    observation = source.observations[0]
    shared_time = Time(sec=7, nanosec=11)
    observation.source_stamp = observation.stamp = shared_time
    source.observations = [observation, observation]
    source.revolution_start = [shared_time, shared_time, shared_time]
    source.observation_filter_stamp = [shared_time, shared_time]
    shared_indices = array.array('I', [0, 1, 2])
    source.revolution_sample_start = source.revolution_sample_end = shared_indices
    cloned = clone_ros_message(source)
    _assert_declared_fields(source, cloned)
    assert cloned.observations[0] is not cloned.observations[1]
    times = [cloned.observations[0].source_stamp, cloned.observations[0].stamp,
             cloned.observations[1].source_stamp, cloned.observations[1].stamp,
             *cloned.revolution_start, *cloned.observation_filter_stamp]
    assert len({id(value) for value in times}) == len(times)
    assert all(value is not shared_time for value in times)
    times[0].nanosec += 1
    assert all(value.nanosec == 11 for value in times[1:])
    assert shared_time.nanosec == 11
    cloned.revolution_sample_start[0] = 9
    assert cloned.revolution_sample_end[0] == shared_indices[0] == 0
    shared_indices[1] = 8
    assert cloned.revolution_sample_start[1] == cloned.revolution_sample_end[1] == 1


@pytest.mark.parametrize('bits', ['7ff8000000000042', 'fff8000000001337'])
def test_distinct_quiet_nan_payload_and_sign_survive_every_declared_float_comparison(
        bits, old_hash_owner):
    value = struct.unpack('!d', bytes.fromhex(bits))[0]
    snapshot = _snapshot(1)
    snapshot.legacy_r_mean_m2 = value
    snapshot.observations[0].phase_disagreement_rad = value
    cloned = clone_ros_message(snapshot)
    _assert_declared_fields(snapshot, cloned)
    assert struct.pack('!d', cloned.legacy_r_mean_m2).hex() == bits
    _assert_declared_fields(snapshot, deserialize_message(serialize_message(cloned), CandidateSnapshot))
    assert snapshot_sha256(cloned) == old_hash_owner.snapshot_sha256(snapshot)


@pytest.mark.parametrize('sec,nanosec', [(-(2**31), 2**32 - 1), (2**31 - 1, 0)])
def test_wire_integer_extrema_copy_without_semantic_time_normalization(sec, nanosec):
    snapshot = _snapshot(1)
    snapshot.schema_version = 2**16 - 1
    snapshot.candidate_id = snapshot.observations[0].source_sequence = 2**64 - 1
    snapshot.observation_filter_state = [255]
    snapshot.revolution_sample_end = [2**32 - 1]
    snapshot.observations[0].stamp = Time(sec=sec, nanosec=nanosec)
    cloned = clone_ros_message(snapshot)
    _assert_declared_fields(snapshot, cloned)
    _assert_declared_fields(snapshot, deserialize_message(serialize_message(cloned), CandidateSnapshot))
    if sec < 0 or nanosec >= 1_000_000_000:
        # Copying a wire representation must not erase the existing semantic
        # rejection at the later canonical evidence boundary.
        with pytest.raises(ValueError):
            snapshot_sha256(cloned)
