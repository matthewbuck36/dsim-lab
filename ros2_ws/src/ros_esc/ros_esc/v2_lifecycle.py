"""Shared deterministic wire identities for opt-in moving fill transactions.

These helpers do not authorize a transaction. Each owner must validate message
identity, finite required geometry, freshness and its own state before mutation.
"""

import hashlib
import math
from collections.abc import Mapping
from functools import lru_cache

from ros_esc.v2_stream import canonical_json, time_to_ns


PROTOCOL_VERSION = 1
SEARCH_EPOCH_TOPIC = '/gesc_gaussian/v2/search_epoch'
DETECTOR_CONFIRMATION_TOPIC = '/gesc_gaussian/v2/detector_confirmation'
CANDIDATE_SNAPSHOT_TOPIC = '/gesc_gaussian/v2/candidate_snapshots'
FILL_COMMAND_TOPIC = '/gesc_gaussian/v2/fill_commands'
FILL_RESULT_TOPIC = '/gesc_gaussian/v2/fill_results'
MAX_COMMANDS = 4096
FRESHNESS_NS = 500_000_000


def message_payload(value, *, exclude=()):
    """Detach a ROS wire value into canonical JSON values, with times as ns.

    Exclusions apply to this outer message only. Optional nonfinite diagnostic
    values become null; callers still must reject nonfinite required fields.
    ROS messages expose fields explicitly, so constants and private state never
    become accidental identity inputs.
    """
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, 'get_fields_and_field_types'):
        fields = value.get_fields_and_field_types()
        if set(fields) == {'sec', 'nanosec'}:
            return time_to_ns(value)
        return {name: message_payload(getattr(value, name))
                for name in fields if name not in exclude}
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError('canonical payload keys must be strings')
        return {key: message_payload(item) for key, item in value.items()
                if key not in exclude}
    if hasattr(value, '__iter__') and not isinstance(value, (bytes, bytearray)):
        return [message_payload(item) for item in value]
    raise TypeError(f'unsupported lifecycle payload type: {type(value).__name__}')


def hash_payload(payload):
    """Hash a detached finite JSON payload; NaN/Infinity are rejected."""
    return hashlib.sha256(canonical_json(payload).encode('utf-8')).hexdigest()


def observation_payload(observation):
    """Preserve source/admission/original receipts, omit transport publication."""
    return message_payload(observation, exclude=('stamp',))


def snapshot_sha256(snapshot):
    payload = message_payload(snapshot, exclude=('stamp', 'evidence_sha256', 'observations'))
    # The former discarded traversal also validated these excluded publication
    # times. Keep that rejection without building every observation twice.
    for observation in snapshot.observations:
        time_to_ns(observation.stamp)
    payload['observations'] = [observation_payload(obs)
                               for obs in snapshot.observations]
    return hash_payload(payload)


# SHA256 of the ordered (field name, declared type) pairs of the supported IDL.
# Slot names and actual SLOT_TYPES are independently checked against these pairs.
# A new interface revision requires explicit review, never an automatic copier.
_CLONE_SCHEMA_SHA256 = (
    'efcfacebe2a3c2debf71bbc0c100396c43ac3ed6bbb95b8d35905b7e41ed1ca6',  # Time
    '4c8d7921a881d819d0fcc55daf5b6a69e10bf59a5ae0bbb83931e48322e001b5',  # Observation
    '9ef758b3b4cf842e78d5ebe59829ac213d7ff0aa09e58ac5fef0a14577b7bfaa',  # Snapshot
    'dff12f53450033ec3fd220ea7132dffc3fe2ea7650fcf9b442a2285658f034fa',  # Command
)


@lru_cache(maxsize=1)
def _structural_clone_plans():
    """Compile immutable, exact-schema instructions; cache no message values."""
    from array import array
    from builtin_interfaces.msg import Time
    from ros_esc_interfaces.msg import CandidateSnapshot, FillCommand, SynchronizedObservation
    from rosidl_parser import definition as idl

    def slot_kind(value):
        if type(value) is idl.BasicType:
            return value.typename
        if type(value) is idl.UnboundedString:
            return 'string'
        if type(value) is idl.NamespacedType and tuple(value.namespaces)[1:] == ('msg',):
            return value.namespaces[0] + '/' + value.name
        if type(value) is idl.UnboundedSequence:
            return 'sequence<' + slot_kind(value.value_type) + '>'
        raise TypeError('unsupported lifecycle slot schema')

    def primitive(expected):
        def copy(value):
            if type(value) is not expected:
                raise TypeError('noncanonical lifecycle primitive type')
            return value
        return copy

    def integer(low, high):
        def copy(value):
            if type(value) is not int:
                raise TypeError('lifecycle integer field is not an int')
            if not low <= value < high:
                raise ValueError('lifecycle integer field outside IDL range')
            return value
        return copy

    def string(value):
        if type(value) is not str:
            raise TypeError('lifecycle string field is not a string')
        if '\x00' in value:
            raise ValueError('embedded NUL in lifecycle message string')
        value.encode('utf-8')  # Reject unpaired surrogates before native publish.
        return value

    def typed_array(typecode, itemsize):
        def copy(value):
            if type(value) is not array or value.typecode != typecode or value.itemsize != itemsize:
                raise TypeError('noncanonical lifecycle typed array')
            return value[:]
        return copy

    def sequence(copy_item):
        def copy(value):
            if type(value) is not list:
                raise TypeError('lifecycle message sequence is not a list')
            return [copy_item(item) for item in value]
        return copy

    def message_copy(kind, instructions):
        def copy(value):
            if type(value) is not kind:
                raise TypeError('unsupported generated lifecycle message type')
            result = object.__new__(kind)
            for slot, copy_field in instructions:
                try:
                    field = getattr(value, slot)
                except AttributeError as exc:
                    raise TypeError('missing declared lifecycle slot') from exc
                setattr(result, slot, copy_field(field))
            return result
        return copy

    copies = {
        'double': primitive(float), 'boolean': primitive(bool), 'string': string,
        'int32': integer(-(2**31), 2**31), 'uint8': integer(0, 2**8),
        'uint16': integer(0, 2**16), 'uint32': integer(0, 2**32),
        'uint64': integer(0, 2**64),
        'sequence<uint8>': typed_array('B', 1),
        'sequence<uint32>': typed_array('I', 4),
    }
    plans = []
    kinds = (Time, SynchronizedObservation, CandidateSnapshot, FillCommand)
    for kind, expected_sha in zip(kinds, _CLONE_SCHEMA_SHA256):
        fields = tuple(kind.get_fields_and_field_types().items())
        slots = tuple('_' + name for name, _ in fields)
        if (hash_payload(fields) != expected_sha or tuple(kind.__slots__) != slots
                or tuple(slot_kind(value) for value in kind.SLOT_TYPES) != tuple(t for _, t in fields)):
            raise TypeError('unsupported generated lifecycle schema')
        instructions = tuple((slot, copies[field_type])
                             for slot, (_, field_type) in zip(slots, fields))
        copy = message_copy(kind, instructions)
        namespace = 'builtin_interfaces' if kind is Time else 'ros_esc_interfaces'
        name = namespace + '/' + kind.__name__
        copies[name] = copy
        copies['sequence<' + name + '>'] = sequence(copy)
        plans.append((kind, fields, slots, copy))
    return tuple(plans), slot_kind


def clone_ros_message(message):
    """Detach supported generated snapshots/commands, preserving every field.

    Copy each nested occurrence independently, including repeated input aliases.
    Only immutable scalar leaves are shared. Private-slot storage avoids default
    constructors but follows explicit IDL representation and range checks.
    """
    plans, slot_kind = _structural_clone_plans()
    if type(message) not in (plans[2][0], plans[3][0]):
        raise TypeError('clone supports only generated CandidateSnapshot and FillCommand')
    # Recheck schemas after compilation too; a warm cache cannot hide drift.
    selected = None
    for kind, fields, slots, copy in plans:
        if (tuple(kind.get_fields_and_field_types().items()) != fields
                or tuple(kind.__slots__) != slots
                or tuple(slot_kind(value) for value in kind.SLOT_TYPES) != tuple(t for _, t in fields)):
            raise TypeError('changed generated lifecycle schema')
        if type(message) is kind:
            selected = copy
    return selected(message)


def result_sha256(result):
    return hash_payload(message_payload(
        result, exclude=('stamp', 'committed_sha256')))


def fill_registry_payload(fills):
    """Exact active law representation used by M2 objective_configuration.

    Accept active GaussianFill wire records. Metadata and publication time are
    excluded because they do not change the composed Gaussian law.
    """
    records = []
    seen = set()
    for fill in fills:
        if isinstance(fill, Mapping):
            expected = {'fill_id', 'cluster_id', 'revision', 'amplitude',
                        'center', 'covariance'}
            if set(fill) != expected:
                raise ValueError('active law mapping has unknown or missing fields')
            identity = int(fill['fill_id'])
            if identity <= 0 or identity in seen:
                raise ValueError('invalid or duplicate active fill identity')
            seen.add(identity)
            records.append(dict(fill))
            continue
        if not fill.active or fill.superseded:
            continue
        identity = int(fill.fill_id)
        if identity <= 0 or identity in seen:
            raise ValueError('invalid or duplicate active fill identity')
        seen.add(identity)
        records.append({
            'fill_id': identity, 'cluster_id': int(fill.cluster_id),
            'revision': int(fill.revision), 'amplitude': float(fill.amplitude),
            'center': [float(fill.center_x), float(fill.center_y)],
            'covariance': [[float(fill.covariance_xx), float(fill.covariance_xy)],
                           [float(fill.covariance_xy), float(fill.covariance_yy)]],
        })
    records.sort(key=lambda record: record['fill_id'])
    # Validate finite law values here rather than converting invalid geometry
    # into the null spelling reserved for optional diagnostic fields.
    canonical_json(records)
    return records


def fill_registry_digest(fills):
    return hash_payload(fill_registry_payload(fills))


def envelope_identity(message):
    """Comparable immutable stream/epoch identity, not a freshness decision."""
    return (int(message.schema_version), str(message.run_id),
            str(message.stream_contract_id), time_to_ns(message.time_origin),
            str(message.frame_id), int(message.search_epoch))


def copy_envelope(target, source):
    """Copy the common lifecycle envelope without aliasing mutable Time fields."""
    from copy import deepcopy
    for field in ('schema_version', 'stamp', 'time_origin', 'run_id',
                  'stream_contract_id', 'frame_id', 'search_epoch'):
        setattr(target, field, deepcopy(getattr(source, field)))
    return target


# R21 uses separate wrapper types. All preceding legacy hashes and clone plans
# intentionally remain unchanged, including decoding old nested CDR messages.
ANGULAR_PROFILES_POLICY = 'angular_profiles_v1'
RECURRENT_TRAPPING_POLICY = 'recurrent_trapping_v1'
RECURRENT_CANDIDATE_SNAPSHOT_TOPIC = '/gesc_gaussian/v2/recurrent_candidate_snapshots'
RECURRENT_FILL_COMMAND_TOPIC = '/gesc_gaussian/v2/recurrent_fill_commands'


def validate_verification_evidence_policy(value, *, simulation,
        continuous_search_mode, metric_mode, motion_mode, algorithm_profile):
    """Exact opt-in selection; legacy policy imposes no new configuration gate."""
    if value == ANGULAR_PROFILES_POLICY:
        return value
    if value != RECURRENT_TRAPPING_POLICY:
        raise ValueError('unsupported v2_verification_evidence_policy')
    if (simulation is not True or algorithm_profile != 'robust_gaussian_v1'
            or continuous_search_mode != 'rolling_gesc_v2'
            or metric_mode != 'recurrent_geometry_v3'
            or motion_mode != 'centered_tracking_v1'):
        raise ValueError('recurrent trapping requires selected robust rolling recurrent centered simulation')
    return value


def recurrent_proof_payload(proof):
    """Freeze only the wrapper's policy and original typed nomination evidence.

    Publication stamps inside the original confirmation/diagnostic are evidence,
    not transport refreshes. The nested snapshot/command has a separate owner.
    A detached proof dictionary is accepted for immutable transaction retention.
    """
    fields = ('schema_version', 'policy_id', 'confirmation', 'diagnostic')
    try:
        value = {key: proof[key] if isinstance(proof, Mapping) else getattr(proof, key)
                 for key in fields}
    except (KeyError, AttributeError, TypeError) as exc:
        raise ValueError('missing recurrent trapping proof') from exc
    if (type(value['schema_version']) is not int or value['schema_version'] != 1
            or value['policy_id'] != RECURRENT_TRAPPING_POLICY):
        raise ValueError('unknown recurrent trapping proof schema or policy')
    for key in ('confirmation', 'diagnostic'):
        if value[key] is None:
            raise ValueError('missing recurrent trapping nomination')
    return message_payload(value)


def recurrent_snapshot_sha256(snapshot, proof):
    """Domain-separated policy/certificate binding without changing old hashing.

    The old snapshot hash excludes its own evidence_sha256, making this safe when
    the selected nested snapshot already stores the resulting wrapper digest.
    """
    return hash_payload(dict(version='recurrent-trapping-snapshot-v1',
        snapshot_sha256=snapshot_sha256(snapshot), proof=recurrent_proof_payload(proof)))


def _clone_recurrent_wrapper(wrapper, *, command):
    from copy import deepcopy
    from ros_esc_interfaces.msg import (RecurrentCandidateSnapshot, RecurrentFillCommand,
                                       DetectorConfirmation, RecurrentConvergenceDiagnostics)
    kind = RecurrentFillCommand if command else RecurrentCandidateSnapshot
    key = 'command' if command else 'snapshot'
    nested = 'FillCommand' if command else 'CandidateSnapshot'
    fields = (('schema_version', 'uint16'), ('policy_id', 'string'),
              (key, 'ros_esc_interfaces/'+nested),
              ('confirmation', 'ros_esc_interfaces/DetectorConfirmation'),
              ('diagnostic', 'ros_esc_interfaces/RecurrentConvergenceDiagnostics'))
    if (type(wrapper) is not kind or tuple(kind.get_fields_and_field_types().items()) != fields
            or type(wrapper.confirmation) is not DetectorConfirmation
            or type(wrapper.diagnostic) is not RecurrentConvergenceDiagnostics):
        raise TypeError('unsupported recurrent trapping wrapper schema')
    recurrent_proof_payload(wrapper)
    result = kind()
    result.schema_version, result.policy_id = wrapper.schema_version, wrapper.policy_id
    setattr(result, key, clone_ros_message(getattr(wrapper, key)))
    # These two certificates are bounded small messages with no observations.
    result.confirmation = deepcopy(wrapper.confirmation)
    result.diagnostic = deepcopy(wrapper.diagnostic)
    return result


def clone_recurrent_snapshot(wrapper):
    return _clone_recurrent_wrapper(wrapper, command=False)


def clone_recurrent_command(wrapper):
    return _clone_recurrent_wrapper(wrapper, command=True)
