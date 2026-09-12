"""M4 complete-objective extraction; analytic inputs and existing evaluators."""

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest
import yaml

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts import v2_direction_reference as reference
from ros_esc.v2_stream import canonical_json, time_to_ns
from ros_esc.v2_direction_policy import POLICY_DIAGNOSTICS_TOPIC
from test_q1_direction_inputs import bag_from_messages, RUN
from test_q2_policy_recording import moving_fixture


BINDING = dict(joint_position_m=[0., 0., .355], rotation_axis=[0., 0., 1.],
               sensor_transform=[[1., 0., 0., .18], [0., 1., 0., 0.],
                                 [0., 0., 1., .015], [0., 0., 0., 1.]])


def fixture(*, affine=True, age=1., decay=.5, maximum_age=30., minimum_norm=1e-4):
    data = moving_fixture()
    messages, metadata, direction, companion = data
    config = metadata['scenario_runner']['v2_identity']['stream_config']
    objective = messages[config['objective_cost_topic']][0][1]
    law = json.loads(objective.objective_config_json)
    law['weights'] = [.8, 1.2, .7]
    law['fills'] = [dict(fill_id=7, cluster_id=3, revision=2, amplitude=.6,
                         center=[.2, -.1], covariance=[[.4, 0.], [0., .2]])]
    law.update(affine_decay_rate=decay, affine_max_age=maximum_age, affine_min_norm=minimum_norm)
    if affine:
        law['affine'] = [dict(cluster_id=3, fill_id=7, direction_revision=4,
            anchor=[.2, -.1], b0=[.3, -.4],
            t0_sec=time_to_ns(objective.composition_stamp)*1e-9-age)]
    bind(data, objective, law)
    return data, objective, law


def bind(data, objective, law):
    """Independent diagonal-Gaussian and affine arithmetic supplies the wire."""
    messages, metadata, direction, companion = data
    config = metadata['scenario_runner']['v2_identity']['stream_config']
    objective.objective_config_json = canonical_json(law)
    objective.objective_sha256 = hashlib.sha256(canonical_json(law).encode()).hexdigest()
    objective.registry_digest = hashlib.sha256(canonical_json(law['fills']).encode()).hexdigest()
    objective.affine_revision = max((item['direction_revision'] for item in law['affine']), default=0)
    objective.sensor_weight, objective.gaussian_weight, objective.affine_weight = law['weights']
    x, y = objective.sensor_x_m[0], objective.sensor_y_m[0]
    gaussian, affine = 0., 0.
    for item in law['fills']:
        gaussian += item['amplitude']*math.exp(-.5*((x-item['center'][0])**2/item['covariance'][0][0]
            +(y-item['center'][1])**2/item['covariance'][1][1]))
    for item in law['affine']:
        age = max(0., time_to_ns(objective.composition_stamp)*1e-9-item['t0_sec'])
        vector = [value*math.exp(-law['affine_decay_rate']*age) for value in item['b0']]
        if ((law['affine_max_age'] <= 0 or age <= law['affine_max_age'])
                and math.hypot(*vector) >= law['affine_min_norm']):
            affine -= sum(value*(coord-anchor) for value, coord, anchor in
                          zip(vector, [x, y], item['anchor']))
    objective.gaussian_cost, objective.affine_cost = [gaussian], [affine]
    total = sum(a*b for a, b in zip(law['weights'], [objective.raw_cost[0], gaussian, affine]))
    objective.augmented_cost = [total]
    messages[config['augmented_cost_topic']][0][1].data = [total]
    direction.observation.augmented_cost = total
    for name in ('objective_revision', 'objective_sha256', 'registry_digest', 'affine_revision',
                 'sensor_weight', 'gaussian_weight', 'affine_weight'):
        setattr(direction, name, getattr(objective, name))
        if hasattr(companion, name): setattr(companion, name, getattr(objective, name))


def normalize(data, **kwargs):
    return analysis.prepare_m4_direction_inputs(bag_from_messages(data[0]), data[1], run_spec=RUN, **kwargs)


def test_filled_affine_rows_retain_complete_law_and_match_existing_reference_at_distinct_angles():
    data, objective, law = fixture()
    rows, result = normalize(data)
    assert result['qualified'], result
    row, = rows
    snapshot = row['objective']
    assert snapshot['component_costs_verified'] and snapshot['effective_affine_count'] == 1
    assert snapshot['affine_terms'][0]['vector'] == pytest.approx([.3*math.exp(-.5), -.4*math.exp(-.5)])
    assert snapshot['objective_sha256'] == objective.objective_sha256
    assert snapshot['registry_digest'] == objective.registry_digest
    assert snapshot['composition_stamp_ns'] == time_to_ns(objective.composition_stamp)
    numerical = reference.augmented_objective(lambda x, y, angle: -2.+.2*math.cos(angle),
        base_xy=[.1, -.3], binding=BINDING, weights=snapshot['weights'],
        gaussian_fills=snapshot['gaussian_fills'], affine_terms=snapshot['affine_terms'])
    for angle in (0., .7, 2.1, 4.5):
        x, y = .1+.18*math.cos(angle), -.3+.18*math.sin(angle)
        gaussian = .6*math.exp(-.5*((x-.2)**2/.4+(y+.1)**2/.2))
        affine = -math.exp(-.5)*(.3*(x-.2)-.4*(y+.1))
        assert numerical(angle) == pytest.approx(.8*(-2.+.2*math.cos(angle))+1.2*gaussian+.7*affine,
                                                rel=1e-13, abs=1e-13)
    json.dumps(rows, allow_nan=False)
    assert row['qualified'] and result['maximum_observations'] == 40000


@pytest.mark.parametrize('age,decay,maximum_age,minimum_norm,kept', [
    (2., 0., 2., .5, 1), (2.0001, 0., 2., .5, 0),
    (2., 0., 0., .5001, 0), (2., 0., 0., .5, 1),
    (-.1, .5, 0., .5, 1), (2., 1., 0., .1, 0),
])
def test_effective_affine_uses_composition_clock_and_strict_owner_boundaries(age, decay, maximum_age, minimum_norm, kept):
    data, objective, law = fixture(age=age, decay=decay, maximum_age=maximum_age, minimum_norm=minimum_norm)
    rows, result = normalize(data)
    assert result['qualified'], result
    assert rows[0]['objective']['effective_affine_count'] == kept
    assert rows[0]['objective']['pruned_affine_count'] == 1-kept


def test_post_fill_empty_affine_does_not_erase_gaussian_and_old_policy_protocol_stays_closed():
    data, _, _ = fixture(affine=False)
    rows, result = normalize(data)
    assert result['qualified'] and rows[0]['objective']['gaussian_fills']
    assert rows[0]['objective']['affine_terms'] == []
    old, denied = analysis.prepare_moving_policy_direction_inputs(
        bag_from_messages(data[0]), data[1], run_spec=RUN)
    assert old == [] and any('objective intervention' in error for error in denied['integrity_errors'])


@pytest.mark.parametrize('fault', ['missing_fill', 'gaussian_cost', 'affine_cost', 'law_hash',
    'registry', 'direction_hash', 'direction_registry', 'affine_revision', 'missing_law',
    'negative_amplitude', 'singular_covariance', 'asymmetric_covariance', 'unbound_affine'])
def test_self_consistent_weighted_cost_cannot_hide_missing_or_changed_augmented_law(fault):
    data, objective, law = fixture()
    if fault == 'missing_fill': law['fills'] = []
    elif fault == 'negative_amplitude': law['fills'][0]['amplitude'] = -.6
    elif fault == 'singular_covariance': law['fills'][0]['covariance'] = [[1., 1.], [1., 1.]]
    elif fault == 'asymmetric_covariance': law['fills'][0]['covariance'] = [[1., .3], [.1, 1.]]
    elif fault == 'unbound_affine': law['affine'][0]['fill_id'] = 99
    elif fault == 'missing_law': law.pop('affine')
    # Changed JSON gets valid outer digests; internal components/geometry must
    # still establish the complete recorded law rather than trust its own hash.
    if fault in ('missing_fill', 'negative_amplitude', 'singular_covariance',
                 'asymmetric_covariance', 'unbound_affine', 'missing_law'):
        objective.objective_config_json = canonical_json(law)
        objective.objective_sha256 = hashlib.sha256(canonical_json(law).encode()).hexdigest()
        objective.registry_digest = hashlib.sha256(canonical_json(law['fills']).encode()).hexdigest()
        for message in (data[2], data[3]):
            message.objective_sha256, message.registry_digest = objective.objective_sha256, objective.registry_digest
    elif fault == 'gaussian_cost': objective.gaussian_cost[0] += .1
    elif fault == 'affine_cost': objective.affine_cost[0] += .1
    elif fault == 'law_hash': objective.objective_sha256 = 'f'*64
    elif fault == 'registry': objective.registry_digest = 'f'*64
    elif fault == 'direction_hash': data[2].objective_sha256 = data[3].objective_sha256 = 'f'*64
    elif fault == 'direction_registry': data[2].registry_digest = data[3].registry_digest = 'f'*64
    elif fault == 'affine_revision':
        objective.affine_revision += 1
        data[2].affine_revision = data[3].affine_revision = objective.affine_revision
    if fault in ('gaussian_cost', 'affine_cost'):
        total = sum(a*b[0] for a, b in zip(law['weights'],
            [objective.raw_cost, objective.gaussian_cost, objective.affine_cost]))
        objective.augmented_cost = [total]
        config = data[1]['scenario_runner']['v2_identity']['stream_config']
        data[0][config['augmented_cost_topic']][0][1].data = [total]
        data[2].observation.augmented_cost = total
    rows, result = normalize(data)
    assert rows == [] and result['integrity_errors'], fault


def test_missing_atomic_objective_never_falls_back_to_raw():
    data, _, _ = fixture()
    config = data[1]['scenario_runner']['v2_identity']['stream_config']
    data[0][config['objective_cost_topic']] = []
    rows, result = normalize(data)
    assert rows == [] and not result['qualified']


@pytest.mark.parametrize('limit', [0, 40001, True, 2.5, '40000'])
def test_m4_extraction_capacity_is_explicit_finite_and_bounded(limit):
    data, _, _ = fixture()
    with pytest.raises(ValueError, match='maximum_observations'):
        normalize(data, maximum_observations=limit)


def test_capacity_counts_unique_inputs_and_quarantines_instead_of_truncating():
    data, _, _ = fixture()
    repeat = deepcopy(data[2]); repeat.diagnostic_sequence += 1
    companion = deepcopy(data[3]); companion.diagnostic_sequence += 1
    data[0]['/gesc_gaussian/v2/direction_diagnostics'].append((20, repeat))
    data[0][POLICY_DIAGNOSTICS_TOPIC].append((21, companion))
    rows, result = normalize(data, maximum_observations=1)
    assert result['qualified'] and len(rows) == 1 and result['duplicate_publications'] == 1
    repeat.observation.source_sequence += 1
    rows, result = normalize(data, maximum_observations=1)
    assert rows == [] and any('capacity exceeded' in error for error in result['integrity_errors'])


@pytest.mark.parametrize('minimum', [-1., float('nan'), float('inf'), True])
def test_residence_extraction_threshold_rejects_invalid(minimum):
    with pytest.raises(ValueError, match='minimum_residence_sec'):
        analysis.label_v2_basin_intervals([], {'basins': []}, minimum_residence_sec=minimum)


def test_residence_default_remains_twelve_and_raw_mode_retains_first_short_opportunity():
    geometry = {'basins': [dict(qualified=True, source_id='first', center_xy=[0., 0.], region_radius_m=.3)]}
    samples = [dict(stamp_ns=t*1_000_000_000, xy=[0., 0.], qualified=True) for t in range(8)]
    assert analysis.label_v2_basin_intervals(samples, geometry) == []
    raw = analysis.label_v2_basin_intervals(samples, geometry, minimum_residence_sec=0.)
    assert raw[0]['duration_sec'] == 7. and not raw[0]['common_support_eligible']
    longer = samples+[dict(stamp_ns=t*1_000_000_000, xy=[0., 0.], qualified=True) for t in range(8, 14)]
    assert analysis.label_v2_basin_intervals(longer, geometry)[0]['duration_sec'] == 13.


@pytest.fixture
def noisy_binding(tmp_path):
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    from test_v2_recording_contract import prepared
    target, metadata, _ = prepared()
    metadata['run_id'] = RUN['run_id']
    description = Path(truth.SENSOR_GEOMETRY_PATH).read_text()
    parameters = {'nodes': {'robot_state_publisher': {'parameters': {
        '/robot_state_publisher': {'ros__parameters': {'robot_description': description}}}}}}
    (tmp_path/'resolved_parameters.yaml').write_text(yaml.safe_dump(parameters))
    repository = next(parent for parent in Path(analysis.__file__).resolve().parents
                      if (parent/'AGENTS.md').is_file())
    launch = repository/'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    selected = [Path(arg.split(':=', 1)[1]) for arg in target
                if arg.startswith(('cost_function_config_filepath:=', 'filter_config_filepath:=',
                                   'sensor_transform_config_filepath:='))]
    def receipt(path):
        return dict(path=str(path.resolve()), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    files = [receipt(path) for path in [launch, Path(truth.SENSOR_GEOMETRY_PATH), *selected]]
    metadata['target_argv'] = target
    (tmp_path/'metadata.yaml').write_text(yaml.safe_dump(metadata))
    baseline = analysis.q1_recorded_binding(tmp_path, source_files=files)
    assert analysis.m4_recorded_binding(tmp_path, source_files=files) == baseline
    # Use a predeclared immutable config file and independently captured bytes.
    expected = tmp_path/'frozen_noise_config.json'
    content = json.loads(selected[0].read_text())
    content['Noise']['params'] = dict(std_dev=.015, seed_num=26090951)
    expected.write_text(json.dumps(content, indent=2)+'\n')
    captured = tmp_path/'resolved_cost_function.json'; captured.write_bytes(expected.read_bytes())
    original = '/tmp/gesc_phase06_declared/resolved_cost_function.json'
    actual = [argument if not argument.startswith('cost_function_config_filepath:=') else
              'cost_function_config_filepath:='+original for argument in target]
    metadata['target_argv'] = actual
    (tmp_path/'metadata.yaml').write_text(yaml.safe_dump(metadata))
    execution = dict(run_id=RUN['run_id'], launch_argv=actual,
        captured_cost_configuration=dict(argv_path=original, **receipt(captured)))
    (tmp_path/'scenario_result.yaml').write_text(yaml.safe_dump(execution))
    return tmp_path, files, receipt(expected), metadata, execution


def test_m4_noisy_binding_preserves_exact_actual_argv_and_captured_selected_model(noisy_binding):
    directory, files, expected, metadata, execution = noisy_binding
    with pytest.raises(ValueError, match='not frozen'):
        analysis.q1_recorded_binding(directory, source_files=files)
    binding = analysis.m4_recorded_binding(directory, source_files=files, expected_cost_configuration=expected)
    model = binding['selected_configurations']['cost_function_config_filepath']
    assert model == dict(path=str(directory/'resolved_cost_function.json'), sha256=expected['sha256'])
    assert binding['settings']['cost_function_config_filepath'] == execution['captured_cost_configuration']['argv_path']
    assert binding['recorded_cost_configuration_path'] == execution['captured_cost_configuration']['argv_path']


@pytest.mark.parametrize('fault', ['changed_capture', 'absent_capture', 'changed_expected',
    'metadata_path', 'execution_path', 'witness_path', 'witness_hash', 'wrong_run',
    'missing_witness', 'changed_source', 'captured_geometry'])
def test_noisy_binding_rejects_config_path_source_or_geometry_substitution(noisy_binding, fault):
    directory, files, expected, metadata, execution = noisy_binding
    if fault == 'changed_capture': (directory/'resolved_cost_function.json').write_text('{}\n')
    elif fault == 'absent_capture': (directory/'resolved_cost_function.json').unlink()
    elif fault == 'changed_expected': Path(expected['path']).write_text('{}\n')
    elif fault == 'metadata_path':
        metadata['target_argv'] = [argument.replace('gesc_phase06_declared', 'gesc_phase06_other')
                                   for argument in metadata['target_argv']]
    elif fault == 'execution_path':
        execution['launch_argv'] = [argument.replace('gesc_phase06_declared', 'gesc_phase06_other')
                                   for argument in execution['launch_argv']]
    elif fault == 'witness_path': execution['captured_cost_configuration']['argv_path'] = '/other.json'
    elif fault == 'witness_hash': execution['captured_cost_configuration']['sha256'] = 'f'*64
    elif fault == 'wrong_run': execution['run_id'] = 'other'
    elif fault == 'missing_witness': execution.pop('captured_cost_configuration')
    elif fault == 'changed_source': files[0]['sha256'] = 'f'*64
    elif fault == 'captured_geometry': (directory/'resolved_parameters.yaml').write_text('nodes: {}\n')
    (directory/'metadata.yaml').write_text(yaml.safe_dump(metadata))
    (directory/'scenario_result.yaml').write_text(yaml.safe_dump(execution))
    with pytest.raises(ValueError):
        analysis.m4_recorded_binding(directory, source_files=files, expected_cost_configuration=expected)


@pytest.mark.parametrize('augmented', [True, False])
def test_d3_objective_payload_is_converted_once_with_full_output_unchanged(monkeypatch, augmented):
    from ros_esc import v2_lifecycle
    from ros_esc_interfaces.msg import ObjectiveCostSample
    data = fixture()[0] if augmented else moving_fixture()
    owner = analysis.prepare_m4_direction_inputs if augmented else analysis.prepare_moving_policy_direction_inputs
    expected = owner(bag_from_messages(data[0]), data[1], run_spec=RUN)
    assert expected[1]['qualified'] and len(expected[0]) == 1
    convert = v2_lifecycle.message_payload
    objectives = []
    def payload(value, **kwargs):
        if isinstance(value, ObjectiveCostSample):
            objectives.append(value)
        return convert(value, **kwargs)
    monkeypatch.setattr(v2_lifecycle, 'message_payload', payload)
    actual = owner(bag_from_messages(data[0]), data[1], run_spec=RUN)
    # Compare the complete normalized observation and qualification, not only
    # its direction vector or selected snapshot fields.
    assert actual == expected
    assert len(objectives) == 1


@pytest.mark.parametrize('fault', ['malformed_law', 'direction_objective_mismatch'])
def test_d3_rejected_objective_never_builds_a_discarded_snapshot(monkeypatch, fault):
    from ros_esc import v2_lifecycle
    from ros_esc_interfaces.msg import ObjectiveCostSample
    data, objective, law = fixture()
    if fault == 'malformed_law':
        objective.objective_config_json = '{'
    else:
        data[2].objective_sha256 = data[3].objective_sha256 = 'f'*64
    convert = v2_lifecycle.message_payload
    objectives = []
    def payload(value, **kwargs):
        if isinstance(value, ObjectiveCostSample):
            objectives.append(value)
        return convert(value, **kwargs)
    monkeypatch.setattr(v2_lifecycle, 'message_payload', payload)
    rows, qualification = normalize(data)
    assert rows == [] and qualification['integrity_errors'] and not qualification['qualified']
    assert objectives == []
