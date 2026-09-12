"""Prospective typed-input normalization; analytic wires, no bags/fields/ROS nodes."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import pytest
from rclpy.serialization import serialize_message, deserialize_message
from ros_esc_interfaces.msg import SynchronizedObservation

from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.v2_lifecycle import observation_payload
from ros_esc.v2_stream import canonical_json, set_time
from test_v2_clock_admission import acquisition_chain


CONTRACT = {'version': analysis.Q1_VERSION}
RUN = {'run_id': 'run_test', 'seed': 26090911, 'partition': 'discovery'}


def typed_fixture(*, ready=True):
    messages, identity, provenance, direction = acquisition_chain()
    config = identity['stream_config']
    objective = messages[config['objective_cost_topic']][0][1]
    law = {'schema_version': 1, 'weights': [1., 1., 0.], 'bias_all_channels': False,
           'fills': [], 'affine': [], 'affine_enabled': True,
           'affine_decay_rate': 5e-7, 'affine_max_age': 35., 'affine_min_norm': 1e-6}
    objective.objective_config_json = canonical_json(law)
    objective.objective_sha256 = hashlib.sha256(objective.objective_config_json.encode()).hexdigest()
    objective.gaussian_cost, objective.augmented_cost = [0.], [-1.]
    messages[config['augmented_cost_topic']][0][1].data = [-1.]
    direction.observation.augmented_cost = -1.
    direction.algorithm_state, direction.algorithm_state_valid = 1, True
    metadata = {'mode': 'simulation', 'algorithm_profile': 'robust_gaussian_v1',
                'scenario_runner': {'v2_identity': identity}}
    return messages, metadata, provenance, objective, direction, ready


def bag_from_messages(messages, ready=True):
    records = {}
    for topic, values in messages.items():
        records[topic] = [BagRecord(topic, type(message).__name__, stamp, None,
                                    None, False, message, ready)
                          for stamp, message in values]
    return BagData(Path('/synthetic'), {}, {
        'v2_direction_diagnostics': {'topic': '/gesc_gaussian/v2/direction_diagnostics'}
    }, records, 0 if ready else None, None)


def normalize(fixture):
    messages, metadata, _, _, _, ready = fixture
    return analysis.prepare_q1_direction_inputs(
        bag_from_messages(messages, ready), metadata, contract=CONTRACT, run_spec=RUN)


def test_schema2_preserves_acquisition_before_covered_clock_and_exact_wire():
    fixture = typed_fixture()
    rows, qualification = normalize(fixture)
    assert qualification['integrity_errors'] == []
    assert qualification['origin_ns'] == rows[0]['stamp_ns'] == 10_250_000_000
    assert rows[0]['receipt_stamp_ns'] == 10_200_000_000 < rows[0]['stamp_ns']
    assert rows[0]['admission_stamp_ns'] == 10_280_000_000
    assert rows[0]['cost_stamp_ns'] == 10_270_000_000
    restored = analysis.q1_observation_from_row(rows[0])
    assert serialize_message(restored) == serialize_message(fixture[4].observation)
    assert observation_payload(deserialize_message(serialize_message(restored), SynchronizedObservation)) \
        == observation_payload(restored)
    json.dumps(rows, allow_nan=False)


@pytest.mark.parametrize('change', ['no_confidence', 'invalid_output', 'weak_output', 'invalid_state'])
def test_anchor_origin_and_input_validity_ignore_method_outcomes(change):
    fixture = typed_fixture()
    direction = fixture[4]
    if change == 'invalid_output':
        direction.output_valid = False
        direction.output_body = [math.nan, math.nan]
    elif change == 'weak_output':
        direction.instant_body = direction.instant_world = direction.output_body = [0., 0.]
        direction.output_magnitude = 0.
    elif change == 'invalid_state':
        direction.algorithm_state_valid = False
    rows, result = normalize(fixture)
    assert result['integrity_errors'] == []
    assert result['origin_ns'] == 10_250_000_000
    assert rows[0]['qualified']
    assert not rows[0]['method']['usable_averaging']


def test_first_publication_is_retained_even_when_later_repeat_has_valid_output():
    fixture = typed_fixture()
    direction = fixture[4]
    later = deepcopy(direction)
    later.diagnostic_sequence = 2
    set_time(later.stamp, 10_300_000_000)
    set_time(later.observation.stamp, 10_300_000_000)
    direction.output_valid = False
    fixture[0]['/gesc_gaussian/v2/direction_diagnostics'].append((6, later))
    rows, result = normalize(fixture)
    assert result['duplicate_publications'] == 1
    assert rows[0]['filter_stamp_ns'] == 10_290_000_000
    assert not rows[0]['method']['output_valid']
    assert rows[0]['method']['v2_output_world'] is None


@pytest.mark.parametrize('fault', ['immutable_repeat', 'objective_digest', 'source_revoke',
                                   'missing_raw', 'source_identity', 'stale_admission',
                                   'nonzero_empty_gaussian', 'incomplete_law'])
def test_ambiguous_or_incomplete_input_quarantines_entire_run(fault):
    fixture = typed_fixture()
    messages, metadata, provenance, objective, direction, _ = fixture
    config = metadata['scenario_runner']['v2_identity']['stream_config']
    if fault == 'immutable_repeat':
        later = deepcopy(direction)
        later.diagnostic_sequence = 2
        later.observation.observation_id = 2
        messages['/gesc_gaussian/v2/direction_diagnostics'].append((6, later))
    elif fault == 'objective_digest':
        objective.objective_sha256 = 'wrong'
    elif fault == 'source_revoke':
        revoked = deepcopy(provenance)
        revoked.source_sequence = 2
        revoked.sensor_transform_valid = False
        messages[config['provenance_topic']].append((6, revoked))
    elif fault == 'missing_raw':
        messages[config['raw_cost_topic']] = []
    elif fault == 'source_identity':
        provenance.run_id = 'another_run'
    elif fault == 'stale_admission':
        set_time(direction.observation.admission_stamp, 11_000_000_000)
    elif fault == 'nonzero_empty_gaussian':
        objective.gaussian_cost = [1.]
    elif fault == 'incomplete_law':
        law = json.loads(objective.objective_config_json)
        law.pop('affine')
        objective.objective_config_json = canonical_json(law)
        objective.objective_sha256 = hashlib.sha256(objective.objective_config_json.encode()).hexdigest()
    rows, result = normalize(fixture)
    assert rows == [] and result['integrity_errors']
    assert result['origin_ns'] is None


def test_cross_topic_bag_receipt_order_does_not_rewrite_owner_receipts():
    fixture = typed_fixture()
    for topic, values in fixture[0].items():
        fixture[0][topic] = [(100-index, msg) for index, (_, msg) in enumerate(values)]
    rows, result = normalize(fixture)
    assert result['integrity_errors'] == []
    assert rows[0]['receipt_stamp_ns'] == 10_200_000_000


def test_pre_readiness_observation_cannot_set_motion_origin():
    rows, result = normalize(typed_fixture(ready=False))
    assert rows[0]['qualified'] and not rows[0]['readiness_eligible']
    assert result['origin_ns'] is None


def test_wire_restoration_rejects_missing_fields():
    rows, _ = normalize(typed_fixture())
    rows[0]['observation_wire'].pop('oldest_receipt_stamp')
    with pytest.raises(ValueError, match='fields'):
        analysis.q1_observation_from_row(rows[0])


def test_q1_common_support_is_explicit_without_changing_historical_default():
    samples = [{'stamp_ns': i*100_000_000, 'qualified': True, 'search_epoch': 'same'}
               for i in range(431)]
    labels = [{'kind': 'positive_basin_residence', 'source_id': 'local',
               'start_ns': 0, 'end_ns': 43_000_000_000}]
    assert not analysis._v2_common_positive_support(samples, labels)[0]
    supported, censored = analysis._v2_common_positive_support(
        samples, labels, minimum_duration_sec=42.)
    assert len(supported) == 1 and not censored


def pose_clock_fixture(*, state_leads=False, fault=None):
    from rosgraph_msgs.msg import Clock
    from ros_esc_interfaces.msg import AlgorithmState
    from std_msgs.msg import Bool
    from ros_esc.v2_stream import time_to_ns
    def record(topic, message, receipt, stamp=None):
        return BagRecord(topic, type(message).__name__, round(receipt*1e9), stamp,
                         None, False, message, True)
    clock_rows = []
    times = [(100., 1.), (100.05, 1.1), (100.10, 1.2)]
    if fault == 'paused':
        times = [(100., 1.), (100.6, 1.1)]
    elif fault == 'rollback':
        times = [(100., 1.), (100.05, .9)]
    elif fault == 'uncovered':
        times = [(100., 1.)]
    for receipt, stamp in times:
        clock = Clock()
        set_time(clock.clock, round(stamp*1e9))
        clock_rows.append(record('/clock', clock, receipt))
    state = AlgorithmState()
    state.run_id, state.run_id_valid = 'run_test', True
    state.algorithm_profile = 'robust_gaussian_v1'
    state.state, state.state_valid = 1, fault != 'invalid_state'
    state.state_elapsed_valid, state.state_elapsed_sec = True, .1 if state_leads else 0.
    set_time(state.stamp, 1_100_000_000 if state_leads else 1_000_000_000)
    state_record = record('/state', state, 100.005 if state_leads else 100., time_to_ns(state.stamp))
    ready_rows = [record('/ready', Bool(data=True), 100.)]
    if fault == 'readiness_pulse':
        ready_rows.extend([record('/ready', Bool(data=False), 100.02),
                           record('/ready', Bool(data=True), 100.03)])
    source = 1_066_666_667 if fault != 'far_future' else 2_000_000_000
    sample = {'stamp_ns': source, 'bag_timestamp_ns': 100_010_000_000,
              'xy': [.25, -.125], 'frame_id': 'odom', 'qualified': True,
              'readiness_eligible': True}
    bag = BagData(Path('/synthetic'), {}, {
        'clock': {'topic': '/clock'}, 'algorithm_state': {'topic': '/state'},
        'recording_ready': {'topic': '/ready'}},
        {'/clock': clock_rows, '/state': [state_record], '/ready': ready_rows}, 100_000_000_000, None)
    return [sample], bag


@pytest.mark.parametrize('state_leads', [False, True])
def test_q1_pose_clock_coverage_preserves_knots_and_original_receipts(state_leads):
    samples, bag = pose_clock_fixture(state_leads=state_leads)
    before = deepcopy(samples)
    masked = analysis.q1_pose_search_eligibility(samples, bag)
    assert samples == before
    assert masked[0]['qualified'] and masked[0]['search_epoch'] == '1'
    assert masked[0]['search_epoch_start_ns'] == 1_000_000_000
    assert masked[0]['stamp_ns'] == samples[0]['stamp_ns']
    assert masked[0]['xy'] == samples[0]['xy']
    assert masked[0]['bag_timestamp_ns'] == 100_010_000_000
    assert masked[0]['admission_bag_timestamp_ns'] == 100_050_000_000
    assert masked[0]['original_receipt_clock_ns'] == 1_000_000_000
    assert not masked[0]['subscriber_timing_reconstructed']


@pytest.mark.parametrize('fault', ['paused', 'rollback', 'uncovered', 'far_future',
                                   'invalid_state', 'readiness_pulse'])
def test_q1_pose_missing_stale_invalid_or_interrupted_support_stays_unavailable(fault):
    samples, bag = pose_clock_fixture(fault=fault)
    row = analysis.q1_pose_search_eligibility(samples, bag)[0]
    assert not row['qualified'] and row['search_epoch'] is None
    assert row['admission_unavailable_reason']


def test_q1_pose_source_regression_is_not_sorted_into_valid_support():
    samples, bag = pose_clock_fixture()
    second = dict(samples[0], stamp_ns=1_050_000_000, bag_timestamp_ns=100_015_000_000)
    result = analysis.q1_pose_search_eligibility(samples+[second], bag)
    assert result[0]['qualified']
    assert result[1]['admission_unavailable_reason'] == 'pose_source_regression_or_duplicate'
