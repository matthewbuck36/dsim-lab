"""Q2 explicit recording identity, paired claims and additive input protocol.

All streams are synthetic generated messages. No bag, field, reference, model,
live graph or historical source-fingerprint fixture is opened by these checks.
"""

from copy import deepcopy
import math

import pytest

from ros_esc.experiment_recording.record_run import (
    applicable_topics, operational_config_for_mode, operational_message_error,
    require_selected_algorithm_topics, resolve_operational_heartbeat_aliases,
    v2_identity_from_metadata, validate_operational_target_coupling,
)
from ros_esc.experiment_recording.validate_run import v2_stream_contract_errors
from ros_esc.experiment_recording.v2_direction_policy_validation import (
    direction_policy_pair_errors, index_policy_companions,
)
from ros_esc.filter_node.rolling_gesc import RollingResult
from ros_esc.filter_node.v2_runtime import policy_diagnostic_message
from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.scenario_runner.run_scenario import build_launch_command, build_metadata
from ros_esc.v2_direction_policy import (
    MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY, POLICY_DIAGNOSTICS_TOPIC, policy_metadata,
)
from ros_esc.v2_stream import set_time
from builtin_interfaces.msg import Time

from test_q1_direction_inputs import CONTRACT, RUN, bag_from_messages, typed_fixture
from test_v2_recording_contract import prepared
from test_v2_source_contract import resolved


DIRECTION_TOPIC = '/gesc_gaussian/v2/direction_diagnostics'


def selected(policy=MOVING_CYCLE_POLICY, delay=0.):
    run = resolved(sensor_delay=delay)
    run['algorithm']['launch_overrides']['v2_direction_policy'] = policy
    target = build_launch_command(run, run_id='run_test')
    metadata = build_metadata(run, 'test', 'q2-policy', '', run_id='run_test')
    _, _, manifest = prepared()
    return target, metadata, manifest


def moving_fixture():
    messages, metadata, provenance, objective, direction, ready = typed_fixture()
    metadata['scenario_runner']['algorithm'] = {
        'launch_overrides': {'v2_direction_policy': MOVING_CYCLE_POLICY}}
    metadata['scenario_runner']['direction_policy'] = policy_metadata(MOVING_CYCLE_POLICY)
    direction.objective_revision = objective.objective_revision
    direction.objective_sha256 = objective.objective_sha256
    direction.registry_digest = objective.registry_digest
    direction.output_units = 'cost_units_per_metre'
    direction.mean_full = direction.coverage_valid = direction.qualified = True
    direction.blend_allowed = True
    direction.cycles_valid = False  # The preserved old control rejects these means.
    direction.completed_revolutions = 3
    direction.sector_counts = [2]*12
    direction.cycle_sector_counts = [2]*36
    direction.cycle_coverage_valid = [True]*3
    direction.cycle_mean_world_x, direction.cycle_mean_world_y = [1., 0., -1.], [0., 1., 0.]
    direction.max_pair_angle_rad = math.pi
    direction.cycle_variability = math.sqrt(8/9)
    direction.magnitude_floor = 3*direction.cycle_variability
    boundaries = [10_000_000_000, 10_075_000_000, 10_150_000_000, 10_225_000_000]
    direction.cycle_start = [set_time(Time(), stamp) for stamp in boundaries[:-1]]
    direction.cycle_end = [set_time(Time(), stamp) for stamp in boundaries[1:]]
    set_time(direction.rolling_start, 10_175_000_000)
    set_time(direction.rolling_end, 10_250_000_000)
    direction.rolling_duration_sec = .075
    direction.phase_start_rad, direction.phase_end_rad = 0., math.tau
    direction.rolling_sample_count = sum(direction.sector_counts)
    direction.max_sample_gap_sec = .004
    direction.instant_body = direction.instant_world = [0., 1.]
    direction.mean_world, direction.mean_magnitude = [1., 0.], 1.
    direction.output_body, direction.output_magnitude = [.75, .25], math.hypot(.75, .25)
    direction.blend_weight = .75
    direction.fallback_used, direction.fallback_reason = False, ''
    margin = math.sqrt(2)*(1e-10+1e-8)
    result = RollingResult(mean_magnitude=1., norm_denominator=2., norm_error=1e-12,
                          coherence=.5, coherence_lower=(1-margin)/(2+1e-12),
                          coherence_upper=(1+margin)/(2-1e-12), coherence_available=True,
                          coherence_reason='', warmup_valid=True,
                          norm_new_evaluations=42, norm_window_evaluations=1008)
    companion = policy_diagnostic_message(direction, result, MOVING_CYCLE_POLICY)
    messages[POLICY_DIAGNOSTICS_TOPIC] = [(7, companion)]
    return messages, metadata, direction, companion


def validate(fixture):
    messages, metadata, _, _ = fixture
    return v2_stream_contract_errors(messages, v2_identity_from_metadata(metadata))


def normalize(fixture):
    messages, metadata, _, _ = fixture
    return analysis.prepare_moving_policy_direction_inputs(
        bag_from_messages(messages), metadata, run_spec=RUN)


@pytest.mark.parametrize('policy', [THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY])
@pytest.mark.parametrize('delay', [0., .1])
def test_selected_argv_metadata_and_conditional_topic_heartbeat_agree(policy, delay):
    target, metadata, manifest = selected(policy, delay)
    identity = v2_identity_from_metadata(metadata)
    assert identity['direction_policy'] == policy_metadata(policy)
    assert f'v2_direction_policy:={policy}' in target
    config = operational_config_for_mode(manifest, 'simulation')
    validate_operational_target_coupling(config, metadata, target)
    aliases = resolve_operational_heartbeat_aliases(config, metadata)
    assert ('v2_direction_policy_diagnostics' in aliases) == (policy == MOVING_CYCLE_POLICY)
    entries = require_selected_algorithm_topics(applicable_topics(manifest, 'simulation'), 'simulation', target)
    companion = next(entry for entry in entries if entry['topic'] == POLICY_DIAGNOSTICS_TOPIC)
    assert companion['required'] == (policy == MOVING_CYCLE_POLICY)
    if policy == MOVING_CYCLE_POLICY:
        assert companion['minimum_messages'] >= 1
        assert companion['singleton_publisher'] and companion['coverage'] == 'motion'
        assert companion['algorithm_required']


@pytest.mark.parametrize('fault', ['missing_metadata', 'wrong_metadata', 'bad_hash', 'missing_argv',
                                   'wrong_argv', 'physical', 'stationary'])
def test_selected_policy_requires_matching_explicit_metadata_and_actual_target(fault):
    target, metadata, manifest = selected()
    if fault == 'missing_metadata':
        metadata['scenario_runner'].pop('direction_policy')
    elif fault == 'wrong_metadata':
        metadata['scenario_runner']['direction_policy'] = policy_metadata(THREE_CYCLE_POLICY)
    elif fault == 'bad_hash':
        metadata['scenario_runner']['direction_policy']['config_sha256'] = '0'*64
    elif fault == 'missing_argv':
        target = [value for value in target if not value.startswith('v2_direction_policy:=')]
    elif fault == 'wrong_argv':
        target = [value.replace(MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY) for value in target]
    elif fault == 'physical':
        metadata['mode'] = 'physical'
    else:
        metadata['scenario_runner']['v2_identity']['continuous_search_mode'] = 'stationary_v1'
    with pytest.raises(ValueError):
        validate_operational_target_coupling(operational_config_for_mode(manifest, 'simulation'), metadata, target)


@pytest.mark.parametrize('fault', ['missing', 'wrong_type'])
def test_new_policy_companion_cannot_be_missing_or_wrong_recorded_wire_type(fault):
    target, _, manifest = selected()
    entries = applicable_topics(manifest, 'simulation')
    if fault == 'missing':
        entries = [entry for entry in entries if entry['topic'] != POLICY_DIAGNOSTICS_TOPIC]
    else:
        entries = deepcopy(entries)
        next(entry for entry in entries if entry['topic'] == POLICY_DIAGNOSTICS_TOPIC)['type'] = 'std_msgs/msg/String'
    with pytest.raises(ValueError):
        require_selected_algorithm_topics(entries, 'simulation', target)


@pytest.mark.parametrize('declared', [None, THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY])
@pytest.mark.parametrize('nested', [THREE_CYCLE_POLICY, MOVING_CYCLE_POLICY])
def test_nested_policy_cannot_override_or_replace_declared_metadata(declared, nested):
    if declared is None:
        _, metadata, _ = prepared()
    else:
        _, metadata, _ = selected(declared)
    metadata['scenario_runner']['v2_identity']['direction_policy'] = policy_metadata(nested)
    with pytest.raises(ValueError, match='scenario_runner sibling'):
        v2_identity_from_metadata(metadata)


def test_default_recording_identity_remains_optional_and_does_not_require_companion():
    target, metadata, manifest = prepared()
    assert 'direction_policy' not in v2_identity_from_metadata(metadata)
    config = operational_config_for_mode(manifest, 'simulation')
    validate_operational_target_coupling(config, metadata, target)
    assert 'v2_direction_policy_diagnostics' not in resolve_operational_heartbeat_aliases(config, metadata)
    entries = [entry for entry in applicable_topics(manifest, 'simulation') if entry['topic'] != POLICY_DIAGNOSTICS_TOPIC]
    require_selected_algorithm_topics(entries, 'simulation', target)


def test_complete_new_pair_accepts_selected_gate_without_old_confidence_and_detaches_protocol():
    fixture = moving_fixture()
    assert validate(fixture) == []
    rows, result = normalize(fixture)
    assert result['integrity_errors'] == []
    assert result['version'] == analysis.MOVING_POLICY_INPUT_VERSION
    assert len(rows) == 1 and rows[0]['qualified']
    assert rows[0]['method']['blend_applied'] and rows[0]['method']['usable_averaging']
    assert rows[0]['method']['direction_policy'] == MOVING_CYCLE_POLICY
    assert rows[0]['method']['v2_output_world'] == [.75, .25]
    assert rows[0]['direction_policy_wire']['diagnostic_sequence'] == 1
    assert rows[0]['first_policy_diagnostic_bag_stamp_ns'] == 7
    assert not fixture[2].cycles_valid


@pytest.mark.parametrize('fault', ['missing', 'conflict', 'orphan', 'same_sequence_later_stamp'])
def test_missing_or_ambiguous_pairs_quarantine_whole_input_run(fault):
    fixture = moving_fixture()
    messages, _, _, companion = fixture
    if fault == 'missing':
        messages[POLICY_DIAGNOSTICS_TOPIC] = []
    elif fault == 'conflict':
        conflicting = deepcopy(companion)
        conflicting.norm_error = 2e-12
        messages[POLICY_DIAGNOSTICS_TOPIC].append((8, conflicting))
    elif fault == 'orphan':
        orphan = deepcopy(companion)
        orphan.diagnostic_sequence += 1
        messages[POLICY_DIAGNOSTICS_TOPIC].append((8, orphan))
    else:
        companion.stamp.nanosec += 1
    assert validate(fixture)
    rows, result = normalize(fixture)
    assert rows == [] and result['integrity_errors'] and result['origin_ns'] is None


@pytest.mark.parametrize('state,state_valid,claimed_permission', [
    (4, True, True), (8, True, True), (99, True, True),
    (1, False, True), (1, True, False),
])
def test_state_permission_conflicts_quarantine_inputs_instead_of_reducing_denominator(
        state, state_valid, claimed_permission):
    fixture = moving_fixture()
    _, _, direction, companion = fixture
    direction.algorithm_state = state
    direction.algorithm_state_valid = state_valid
    direction.blend_allowed = companion.blend_allowed = claimed_permission
    assert validate(fixture)
    rows, result = normalize(fixture)
    assert rows == [] and result['integrity_errors']


def test_exact_duplicate_companion_keeps_first_recorded_receipt():
    fixture = moving_fixture()
    fixture[0][POLICY_DIAGNOSTICS_TOPIC].append((8, deepcopy(fixture[3])))
    index, errors = index_policy_companions(fixture[0][POLICY_DIAGNOSTICS_TOPIC])
    assert not errors and len(index) == 1
    rows, result = normalize(fixture)
    assert not result['integrity_errors'] and rows[0]['first_policy_diagnostic_bag_stamp_ns'] == 7


@pytest.mark.parametrize('field,value', [
    ('run_id', 'other'), ('source_schema_version', 1), ('policy_schema_version', 2),
    ('policy_config_sha256', '0'*64), ('direction_policy', THREE_CYCLE_POLICY),
    ('output_units', 'cost'), ('configured_mean_weight', .5), ('actual_blend_weight', .5),
    ('coherence_threshold', .2), ('source_sequence', 99), ('observation_id', 99),
    ('objective_sha256', '1'*64), ('reset_sequence', 99), ('reset_reason', 'other'),
])
def test_companion_identity_and_configuration_never_inferred_from_output(field, value):
    fixture = moving_fixture()
    setattr(fixture[3], field, value)
    assert validate(fixture)
    with pytest.raises(ValueError):
        analysis.direction_method_for_policy(fixture[2], policy_record=policy_metadata(MOVING_CYCLE_POLICY),
                                             companion=fixture[3])


@pytest.mark.parametrize('fault', ['empty', 'old_end', 'duration', 'phase', 'samples', 'gap'])
def test_false_current_cycle_support_claims_are_rejected(fault):
    fixture = moving_fixture()
    _, _, direction, companion = fixture
    if fault == 'empty':
        direction.rolling_start = companion.rolling_start = deepcopy(direction.rolling_end)
    elif fault == 'old_end':
        direction.rolling_end = companion.rolling_end = set_time(Time(), 10_249_000_000)
    elif fault == 'duration': direction.rolling_duration_sec = .074
    elif fault == 'phase': direction.phase_end_rad = math.pi
    elif fault == 'samples': direction.rolling_sample_count += 1
    else: direction.max_sample_gap_sec = .501
    assert validate(fixture)
    rows, result = normalize(fixture)
    assert rows == [] and result['integrity_errors']


@pytest.mark.parametrize('fault', ['lower', 'upper', 'error', 'denominator', 'mean', 'margin',
                                   'new_budget', 'window_budget', 'warmup', 'cycle_gap',
                                   'cycle_future', 'false_unqualified', 'false_weight', 'output_algebra'])
def test_false_numerical_and_gate_claims_are_rejected(fault):
    fixture = moving_fixture()
    _, _, direction, companion = fixture
    if fault == 'lower': companion.coherence_lower = .8
    elif fault == 'upper': companion.coherence_upper = .1
    elif fault == 'error': companion.norm_error = 1e-9
    elif fault == 'denominator': companion.norm_denominator = .1
    elif fault == 'mean': direction.mean_magnitude = companion.mean_magnitude = 2.
    elif fault == 'margin': companion.numerator_margin = 0.
    elif fault == 'new_budget': companion.norm_new_evaluations = 2049
    elif fault == 'window_budget': companion.norm_window_evaluations = 20001
    elif fault == 'warmup': companion.warmup_valid = False
    elif fault == 'cycle_gap': direction.cycle_start[1].nanosec += 1
    elif fault == 'cycle_future': set_time(direction.cycle_end[-1], 10_251_000_000)
    elif fault == 'false_unqualified': direction.qualified = companion.selected_policy_qualified = False
    elif fault == 'false_weight': direction.blend_weight = companion.actual_blend_weight = .5
    else:
        direction.output_body = [.2, .8]
        direction.output_magnitude = math.hypot(.2, .8)
    assert validate(fixture)
    with pytest.raises(ValueError):
        analysis.direction_method_for_policy(direction, policy_record=policy_metadata(MOVING_CYCLE_POLICY),
                                             companion=companion)


def test_startup_heartbeat_checks_identity_but_does_not_require_qualified_mean():
    fixture = moving_fixture()
    identity = v2_identity_from_metadata(fixture[1])
    companion = fixture[3]
    companion.selected_policy_qualified = companion.output_valid = companion.warmup_valid = False
    assert operational_message_error('v2_direction_policy_diagnostics', companion, 'simulation',
                                     'robust_gaussian_v1', identity, 10_000_000_000) is None
    companion.policy_config_sha256 = '0'*64
    assert operational_message_error('v2_direction_policy_diagnostics', companion, 'simulation',
                                     'robust_gaussian_v1', identity, 10_000_000_000)


def test_first_direction_publication_is_retained_even_when_later_repeat_is_usable():
    fixture = moving_fixture()
    messages, _, direction, companion = fixture
    later, later_companion = deepcopy(direction), deepcopy(companion)
    later.diagnostic_sequence = later_companion.diagnostic_sequence = 2
    set_time(later.stamp, 10_300_000_000)
    set_time(later.observation.stamp, 10_300_000_000)
    set_time(later_companion.stamp, 10_300_000_000)
    direction.output_valid = companion.output_valid = False
    direction.blend_weight = companion.actual_blend_weight = 0.
    messages[DIRECTION_TOPIC].append((9, later))
    messages[POLICY_DIAGNOSTICS_TOPIC].append((10, later_companion))
    rows, result = normalize(fixture)
    assert not result['integrity_errors'] and result['duplicate_publications'] == 1
    assert len(rows) == 1 and rows[0]['method']['diagnostic_sequence'] == 1
    assert not rows[0]['method']['output_valid'] and not rows[0]['method']['usable_averaging']
    assert rows[0]['first_policy_diagnostic_bag_stamp_ns'] == 7


def test_old_input_protocol_refuses_new_metadata_and_old_guard_refuses_new_weight():
    fixture = moving_fixture()
    with pytest.raises(ValueError, match='input protocol'):
        analysis.prepare_q1_direction_inputs(bag_from_messages(fixture[0]), fixture[1],
                                            contract=CONTRACT, run_spec=RUN)
    identity = v2_identity_from_metadata(fixture[1])
    identity.pop('direction_policy')
    assert v2_stream_contract_errors(fixture[0], identity)
    old = typed_fixture()
    with pytest.raises(ValueError, match='input protocol'):
        analysis.prepare_moving_policy_direction_inputs(bag_from_messages(old[0]), old[1], run_spec=RUN)
    assert analysis.direction_method_for_policy(old[4]) == analysis._q1_method(old[4])


def test_eligible_mean_cannot_silently_bypass_fixed_selected_weight():
    fixture = moving_fixture()
    _, _, direction, companion = fixture
    direction.blend_weight = companion.actual_blend_weight = 0.
    direction.fallback_used = companion.fallback_used = True
    direction.fallback_reason = companion.fallback_reason = 'unexplained_fallback'
    direction.output_body, direction.output_magnitude = [0., 1.], 1.
    assert validate(fixture)
    with pytest.raises(ValueError, match='bypassed'):
        analysis.direction_method_for_policy(direction, policy_record=policy_metadata(MOVING_CYCLE_POLICY),
                                             companion=companion)


def test_malformed_companion_timestamp_quarantines_inputs_without_raising():
    fixture = moving_fixture()
    fixture[3].stamp.nanosec = 1_000_000_000
    rows, result = normalize(fixture)
    assert rows == [] and result['integrity_errors']


def test_original_receipt_before_origin_is_valid_when_admitted_source_is_covered():
    """Callback-entry receipt may precede origin while its later admission does not."""
    from ros_esc.filter_node.rolling_gesc import (
        AugmentedCost, EncoderSample, ObjectiveIdentity, PoseSample, Provenance,
        RawCost, SourceSynchronizer, StreamIdentity,
    )
    from ros_esc.v2_stream import stream_contract_id

    fixture = moving_fixture()
    _, metadata, direction, _ = fixture
    config = metadata['scenario_runner']['v2_identity']['stream_config']
    origin, receipt, source, now = 10_000_000_000, 9_990_000_000, 10_250_000_000, 10_280_000_000
    identity = StreamIdentity('run_test', stream_contract_id(config, origin), 'odom', origin,
                              cost_key_basis='model_input_time')
    core = SourceSynchronizer()
    core.set_context(identity)
    for stamp in (source-10_000_000, source+10_000_000):
        assert not core.add_pose(PoseSample(stamp, (0., 0.), 0., receipt, 'odom'), now).faults
    assert not core.add_encoder(EncoderSample(source, 0., receipt), now).faults
    assert not core.add_raw_cost(RawCost(.25, (-1.,), receipt), now).faults
    assert not core.add_augmented(AugmentedCost(.25, (-1.,), ObjectiveIdentity(1), receipt), now).faults
    batch = core.add_provenance(Provenance(.25, 1, source, 10_270_000_000,
                                          (.18, 0.), 0., identity, receipt), now)
    assert not batch.faults and len(batch.observations) == 1
    actual = batch.observations[0]
    assert actual.oldest_receipt_stamp_ns == actual.receipt_stamp_ns == receipt < origin
    assert actual.admission_stamp_ns == now >= origin
    set_time(direction.observation.receipt_stamp, actual.receipt_stamp_ns)
    set_time(direction.observation.oldest_receipt_stamp, actual.oldest_receipt_stamp_ns)
    assert validate(fixture) == []
    rows, result = normalize(fixture)
    assert not result['integrity_errors']
    assert rows[0]['oldest_receipt_stamp_ns'] == receipt
