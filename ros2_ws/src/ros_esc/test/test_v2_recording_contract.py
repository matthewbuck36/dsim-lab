"""Selected V2 recorder identity and additive typed evidence gates."""

from copy import deepcopy
import hashlib
import math
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from nav_msgs.msg import Odometry

from ros_esc.experiment_recording.record_run import (
    applicable_topics, load_manifest, operational_config_for_mode,
    operational_message_error, require_selected_algorithm_topics,
    resolve_operational_heartbeat_aliases, validate_operational_target_coupling,
    v2_message_identity_error,
)
from ros_esc.experiment_recording.validate_run import v2_stream_contract_errors
from ros_esc.scenario_runner.run_scenario import build_launch_command, build_metadata
from ros_esc.v2_stream import canonical_json, set_time, stream_contract_id
from ros_esc_interfaces.msg import (
    AlgorithmState, GescDirectionDiagnostics, ObjectiveCostSample,
    SourceSampleProvenance, StampedFloat64MultiArray, Timekeeper,
)
from test_v2_source_contract import resolved

PACKAGE = Path(__file__).parents[1]
MANIFEST = PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml'


def prepared(delay=.0):
    run = resolved(sensor_delay=delay)
    target = build_launch_command(run, run_id='run_test')
    metadata = build_metadata(run, 'test', 'v2', '', run_id='run_test')
    manifest = load_manifest(MANIFEST)
    return target, metadata, manifest


@pytest.mark.parametrize('delay', [0., .1])
def test_selected_streams_required_and_startup_heartbeats_include_exact_provenance(delay):
    target, metadata, manifest = prepared(delay)
    operational = operational_config_for_mode(manifest, 'simulation')
    aliases = resolve_operational_heartbeat_aliases(operational, metadata)
    expected = 'v2_source_provenance_delayed' if delay else 'v2_source_provenance'
    assert expected in aliases
    assert 'v2_objective_cost' in aliases and 'v2_direction_diagnostics' in aliases
    entries = require_selected_algorithm_topics(applicable_topics(manifest, 'simulation'), 'simulation', target)
    selected = {entry['alias']: entry for entry in entries}
    assert selected[expected]['required']
    assert selected['v2_source_provenance']['required']
    assert selected['v2_objective_cost']['required']
    assert selected['v2_direction_diagnostics']['required']
    validate_operational_target_coupling(operational, metadata, target)
    legacy = [arg for arg in target if not arg.startswith(('continuous_search_mode:=', 'v2_'))]
    legacy_entries = require_selected_algorithm_topics(applicable_topics(manifest, 'simulation'), 'simulation', legacy)
    assert not next(entry for entry in legacy_entries if entry['alias'] == 'v2_direction_diagnostics')['required']


def test_selection_requires_retained_metadata_and_matching_run_topic_identity():
    target, metadata, manifest = prepared()
    operational = operational_config_for_mode(manifest, 'simulation')
    for changed in (
        [arg.replace('v2_run_id:=run_test', 'v2_run_id:=wrong_run') for arg in target],
        [arg.replace('algorithm_pose_topic:=/odom', 'algorithm_pose_topic:=/wrong_pose') for arg in target],
    ):
        with pytest.raises(ValueError, match='V2'):
            validate_operational_target_coupling(operational, metadata, changed)
    metadata['scenario_runner'].pop('v2_identity')
    with pytest.raises(ValueError, match='identity metadata'):
        validate_operational_target_coupling(operational, metadata, target)


def chain():
    _, metadata, _ = prepared()
    identity = metadata['scenario_runner']['v2_identity']
    config = identity['stream_config']
    # This retained fixture intentionally exercises publication-key schema 1.
    # The selected runner now emits schema 2; its acquisition-key tests are separate.
    config['schema_version'] = 1
    config.pop('cost_key_basis')
    origin, source_ns, cost_ns, composition_ns, output_ns = (
        10_000_000_000, 10_250_000_000, 10_270_000_000, 10_280_000_000, 10_290_000_000,
    )
    def envelope(message, stamp):
        message.schema_version = 1
        set_time(message.stamp, stamp)
        set_time(message.time_origin, origin)
        message.run_id, message.frame_id = 'run_test', 'odom'
        message.stream_contract_id = stream_contract_id(config, origin)
        return message
    provenance = envelope(SourceSampleProvenance(), cost_ns)
    provenance.source_sequence = 1
    set_time(provenance.model_input_stamp, source_ns)
    set_time(provenance.cost_publication_stamp, cost_ns)
    provenance.legacy_cost_source_timestamp_sec = .27
    provenance.channel_count = 1
    provenance.sensor_x_m, provenance.sensor_y_m, provenance.sensor_world_phase_rad = [.18], [0.], [0.]
    provenance.model_input_stamp_valid = provenance.sensor_transform_valid = True
    objective = envelope(ObjectiveCostSample(), composition_ns)
    objective.source_sequence = 1
    set_time(objective.model_input_stamp, source_ns)
    set_time(objective.composition_stamp, composition_ns)
    objective.legacy_cost_source_timestamp_sec = .27
    objective.channel_count = objective.objective_revision = 1
    configuration = {'fills': [], 'weights': [1., 1., 0.]}
    objective.objective_config_json = canonical_json(configuration)
    objective.objective_sha256 = hashlib.sha256(objective.objective_config_json.encode()).hexdigest()
    objective.registry_digest = hashlib.sha256(canonical_json([]).encode()).hexdigest()
    objective.sensor_weight, objective.gaussian_weight, objective.affine_weight = configuration['weights']
    objective.sensor_x_m, objective.sensor_y_m = [.18], [0.]
    objective.raw_cost, objective.gaussian_cost, objective.affine_cost, objective.augmented_cost = [-1.], [.2], [0.], [-.8]
    objective.valid = True
    direction = envelope(GescDirectionDiagnostics(), output_ns)
    direction.diagnostic_sequence = 1
    observation = envelope(direction.observation, output_ns)
    for name, stamp in (
        ('source_stamp', source_ns), ('cost_source_stamp', cost_ns),
        ('pose_left_stamp', source_ns-10_000_000), ('pose_right_stamp', source_ns+10_000_000),
        ('encoder_left_stamp', source_ns), ('encoder_right_stamp', source_ns),
        ('receipt_stamp', composition_ns), ('oldest_receipt_stamp', source_ns-10_000_000),
    ):
        set_time(getattr(observation, name), stamp)
    observation.legacy_cost_source_timestamp_sec = .27
    observation.source_sequence = observation.objective_revision = observation.observation_id = 1
    observation.sensor_transform_observed = observation.demodulation_phase_reconstructed = True
    observation.sync_error_sec = .01
    observation.raw_cost_valid = observation.augmented_cost_valid = observation.synchronized_valid = True
    observation.raw_cost, observation.augmented_cost, observation.sensor_x_m = -1., -.8, .18
    direction.instant_body = direction.instant_world = direction.output_body = [1., 0.]
    direction.output_magnitude = 1.
    direction.output_valid = True
    set_time(direction.output_pose_stamp, composition_ns)
    poses = []
    for stamp in (source_ns-10_000_000, source_ns+10_000_000, composition_ns):
        pose = Odometry()
        pose.header.frame_id = 'odom'
        set_time(pose.header.stamp, stamp)
        pose.pose.pose.orientation.w = 1.
        poses.append((0, pose))
    messages = {
        config['pose_topic']: poses,
        config['encoder_topic']: [(0, StampedFloat64MultiArray(timestamp=.25, data=[0.]))],
        config['timekeeper_topic']: [(0, Timekeeper(mode='sim time', start_time=10.))],
        config['raw_cost_topic']: [(1, StampedFloat64MultiArray(timestamp=.27, data=[-1.]))],
        config['augmented_cost_topic']: [(2, StampedFloat64MultiArray(timestamp=.27, data=[-.8]))],
        config['provenance_topic']: [(3, provenance)],
        config['objective_cost_topic']: [(4, objective)],
        '/gesc_gaussian/v2/direction_diagnostics': [(5, direction)],
    }
    return messages, identity, provenance, objective, direction


def test_complete_typed_chain_valid_without_direction_confidence():
    messages, identity, provenance, objective, direction = chain()
    assert v2_stream_contract_errors(messages, identity) == []
    assert not direction.qualified
    assert operational_message_error('v2_direction_diagnostics', direction, 'simulation', 'robust_gaussian_v1', identity, 10_000_000_000) is None
    assert operational_message_error('v2_source_provenance', provenance, 'simulation', 'robust_gaussian_v1', identity, 10_000_000_000) is None


def test_invalid_startup_direction_can_be_unbound_but_cannot_authorize_readiness():
    messages, identity, _, _, direction = chain()
    direction.stream_contract_id = ''
    direction.output_valid = direction.observation.synchronized_valid = False
    assert v2_stream_contract_errors(messages, identity) == []
    assert operational_message_error('v2_direction_diagnostics', direction, 'simulation', 'robust_gaussian_v1', identity, 10_000_000_000)


@pytest.mark.parametrize('mutate,expected', [
    (lambda p,o,d: setattr(p, 'run_id', 'other'), 'identity'),
    (lambda p,o,d: setattr(o, 'sensor_x_m', [1.]), 'geometry'),
    (lambda p,o,d: setattr(o, 'augmented_cost', [-.7]), 'legacy'),
    (lambda p,o,d: setattr(o, 'objective_sha256', 'bad'), 'digest'),
    (lambda p,o,d: setattr(d, 'qualified', True), 'coverage'),
    (lambda p,o,d: setattr(d, 'blend_weight', .5), 'qualification'),
    (lambda p,o,d: setattr(d, 'output_body', [0., 1.]), 'rotation'),
    (lambda p,o,d: set_time(d.observation.pose_right_stamp, 10_301_000_000), 'brackets'),
    (lambda p,o,d: setattr(d.observation, 'sensor_transform_observed', False), 'admitted'),
])
def test_corrupt_claims_fail_independently(mutate, expected):
    messages, identity, provenance, objective, direction = chain()
    mutate(provenance, objective, direction)
    assert any(expected in error for error in v2_stream_contract_errors(messages, identity))


def test_atomic_metadata_cannot_replace_selected_raw_admission():
    messages, identity, _, _, _ = chain()
    messages[identity['stream_config']['raw_cost_topic']] = []
    assert any('selected raw' in error for error in v2_stream_contract_errors(messages, identity))


def test_timekeeper_origin_conflict_fails_even_when_old_origin_is_restored():
    messages, identity, _, _, _ = chain()
    messages[identity['stream_config']['timekeeper_topic']].extend([
        (10, Timekeeper(mode='sim time', start_time=11.)),
        (11, Timekeeper(mode='sim time', start_time=10.)),
    ])
    assert any('immutable' in error for error in v2_stream_contract_errors(messages, identity))


@pytest.mark.parametrize('corrupt', ['zero_cycles', 'variance', 'pair_angle', 'mean_norm', 'instant_frame', 'phase', 'stale_source', 'stale_pose', 'oldest_receipt', 'missing_bracket'])
def test_validator_recomputes_confidence_and_current_frame_claims(corrupt):
    messages, identity, _, _, direction = chain()
    direction.qualified = direction.mean_full = direction.coverage_valid = direction.cycles_valid = True
    direction.sector_counts = [2]*12
    direction.cycle_sector_counts = [2]*36
    direction.cycle_coverage_valid = [True]*3
    direction.cycle_mean_world_x = [1.,1.,1.]
    direction.cycle_mean_world_y = [0.,0.,0.]
    direction.mean_world = [1.,0.]
    direction.mean_magnitude = 1.
    direction.magnitude_floor = 1e-6
    assert v2_stream_contract_errors(messages,identity) == []
    if corrupt == 'zero_cycles':
        direction.cycle_mean_world_x = [0.,0.,0.]
    elif corrupt == 'variance':
        direction.cycle_mean_world_x = [1.,1.,2.]
    elif corrupt == 'pair_angle':
        # Small disagreement passes the numerical gate but falsifies declared 0.
        direction.cycle_mean_world_x = [1.,math.cos(.01),1.]
        direction.cycle_mean_world_y = [0.,math.sin(.01),0.]
        cx = sum(direction.cycle_mean_world_x)/3
        cy = sum(direction.cycle_mean_world_y)/3
        direction.cycle_variability = math.sqrt(sum((x-cx)**2+(y-cy)**2 for x,y in zip(direction.cycle_mean_world_x,direction.cycle_mean_world_y))/3)
        direction.magnitude_floor = 3*direction.cycle_variability
    elif corrupt == 'mean_norm':
        direction.mean_world = [.5,0.]
    elif corrupt == 'instant_frame':
        direction.instant_body = [0.,1.]
    elif corrupt == 'phase':
        direction.observation.sensor_phase_rad = .2
    elif corrupt == 'stale_source':
        set_time(direction.stamp,10_760_000_000)
        set_time(direction.observation.oldest_receipt_stamp,10_280_000_000)
    elif corrupt == 'stale_pose':
        set_time(direction.output_pose_stamp,9_700_000_000)
    elif corrupt == 'oldest_receipt':
        set_time(direction.observation.oldest_receipt_stamp,9_000_000_000)
    elif corrupt == 'missing_bracket':
        messages[identity['stream_config']['encoder_topic']] = []
    assert v2_stream_contract_errors(messages,identity)
