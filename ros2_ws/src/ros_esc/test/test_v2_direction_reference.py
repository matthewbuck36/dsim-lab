"""Analytical M2 references: no retained bag/model cost evaluation."""

from copy import deepcopy
from dataclasses import replace
import json
import hashlib
import math
from pathlib import Path
from types import SimpleNamespace as NS
import warnings

import numpy as np
import pytest
from scipy.integrate import IntegrationWarning

from ros_esc.plotting_scripts import v2_direction_reference as reference


def _harmonics(function):
    return reference.integrate_stationary_harmonics(function, xy=[0, 0], sources=[])


def _binding():
    transform = np.eye(4)
    transform[:3, 3] = [.18, 0, .015]
    return {'joint_position_m': [0, 0, .355], 'rotation_axis': [0, 0, 1],
            'sensor_transform': transform.tolist()}


@pytest.mark.parametrize('a,b', [(1, 0), (0, 1), (1, 2), (-2, .25)])
def test_first_harmonics_keep_selected_sign_and_cross_axis(a, b):
    harmonics = _harmonics(lambda theta: 3 + a*math.cos(theta)+b*math.sin(theta))
    assert harmonics['qualified']
    assert [harmonics['coefficients'][key]['value'] for key in ('mean', 'cosine', 'sine')] \
        == pytest.approx([3, a, b], abs=1e-12)
    result = reference.stationary_reference(harmonics, omega_rad_sec=math.tau/3)
    transfer = complex(.8143503760075071, .38882366325101514)
    assert result['informative']
    assert result['world_vector'] == pytest.approx([
        -(transfer.real*a+transfer.imag*b)/.18,
        -(transfer.real*b-transfer.imag*a)/.18], abs=1e-12)


@pytest.mark.parametrize('function', [lambda theta: 4.0,
                                    lambda theta: math.cos(2*theta),
                                    lambda theta: 1+math.sin(7*theta)])
def test_dc_and_higher_harmonics_do_not_manufacture_direction(function):
    result = reference.stationary_reference(_harmonics(function), omega_rad_sec=math.tau/3)
    assert result['qualified'] and not result['informative']
    assert result['magnitude'] < 1e-12


def test_signed_rate_reversal_changes_washout_cross_axis():
    harmonic = _harmonics(math.cos)
    ccw = reference.stationary_reference(harmonic, omega_rad_sec=math.tau/3)
    cw = reference.stationary_reference(harmonic, omega_rad_sec=-math.tau/3)
    assert cw['world_vector'] == pytest.approx([ccw['world_vector'][0], -ccw['world_vector'][1]])


def test_rotated_angular_objective_rotates_reference():
    yaw = 1.31
    original = reference.stationary_reference(_harmonics(math.cos), omega_rad_sec=2)
    rotated = reference.stationary_reference(_harmonics(lambda theta: math.cos(theta-yaw)),
                                               omega_rad_sec=2)
    x, y = original['world_vector']
    assert rotated['world_vector'] == pytest.approx([
        x*math.cos(yaw)-y*math.sin(yaw), x*math.sin(yaw)+y*math.cos(yaw)])


def test_discrete_transfer_tends_to_continuous_and_keeps_output_before_update():
    omega = math.tau/3
    continuous = reference.continuous_transfer(omega)
    errors = [abs(reference.discrete_transfer(omega, step)-continuous)
              for step in (.05, .01, .001)]
    assert errors[0] > errors[1] > errors[2]
    assert reference.discrete_transfer(omega, .01) == pytest.approx(
        complex(.8169257178, .3919990354), abs=1e-10)


@pytest.mark.parametrize('step', [0, -1, 2, 3, math.nan, math.inf])
def test_unstable_or_invalid_euler_step_is_rejected(step):
    with pytest.raises(ValueError):
        reference.discrete_transfer(2, step)


def test_dual_adaptive_integral_resolves_narrow_analytic_peak():
    # Shifted Poisson kernel: exact mean1 and first-harmonic coefficients2r.
    radius, angle = .97, math.radians(3.7)
    def poisson(theta):
        return (1-radius**2)/(1-2*radius*math.cos(theta-angle)+radius**2)
    receipt = _harmonics(poisson)
    assert receipt['qualified']
    expected = [1, 2*radius*math.cos(angle), 2*radius*math.sin(angle)]
    assert [receipt['coefficients'][key]['value'] for key in ('mean', 'cosine', 'sine')] \
        == pytest.approx(expected, abs=1e-8)
    passes = receipt['coefficients']['mean']['passes']
    assert passes[0]['breakpoints_rad'] != passes[1]['breakpoints_rad']
    assert receipt['objective_evaluations'] < 25000


@pytest.mark.parametrize('fault', ['warning', 'message', 'nonfinite', 'error', 'disagreement'])
def test_failed_integral_remains_unavailable(monkeypatch, fault):
    calls = []
    def fake_quad(function, *args, **kwargs):
        calls.append(kwargs)
        if fault == 'warning':
            warnings.warn('unresolved quadrature', IntegrationWarning)
        value = math.nan if fault == 'nonfinite' else (
            .001 if fault == 'disagreement' and len(calls) % 2 == 0 else 0.0)
        result = (value, .001 if fault == 'error' else 1e-15, {'neval': 20})
        return result + ('failed integration',) if fault == 'message' else result
    monkeypatch.setattr(reference, 'quad', fake_quad)
    result = _harmonics(math.cos)
    assert not result['qualified']
    assert len(calls) == 6
    assert not reference.stationary_reference(result, omega_rad_sec=2)['informative']


def test_objective_budget_and_nonfinite_values_fail_closed(monkeypatch):
    monkeypatch.setattr(reference, 'MAXIMUM_OBJECTIVE_EVALUATIONS', 2)
    assert not _harmonics(math.cos)['qualified']
    monkeypatch.setattr(reference, 'MAXIMUM_OBJECTIVE_EVALUATIONS', 25000)
    assert not _harmonics(lambda angle: math.inf)['qualified']


def test_source_bearings_appear_in_both_partitions():
    result = reference.integrate_stationary_harmonics(
        math.cos, xy=[0, 0], sources=[{'x_m': 1, 'y_m': 2}])
    bearing = math.atan2(2, 1)
    for coefficient in result['coefficients'].values():
        for item in coefficient['passes']:
            assert bearing in item['breakpoints_rad']
            assert bearing+math.pi in item['breakpoints_rad']


def test_informative_gate_uses_reference_numerical_error():
    harmonic = _harmonics(lambda theta: 1e-6*math.cos(theta))
    for key in ('cosine', 'sine'):
        harmonic['coefficients'][key]['error'] = 1e-6
    result = reference.stationary_reference(harmonic, omega_rad_sec=2)
    assert result['qualified'] and not result['informative']
    assert result['informative_threshold'] == pytest.approx(20*result['estimated_vector_error'])
    assert reference.angular_error_deg([0, 0], [1, 0]) is None


def test_augmented_reference_uses_rotating_sensor_gaussian_and_affine():
    binding = _binding()
    center = [.18, 0]
    objective = reference.augmented_objective(
        lambda x, y, theta: 0, base_xy=[0, 0], binding=binding, weights=[0, 1, 1],
        gaussian_fills=[{'center': center, 'covariance': [[.01, 0], [0, .01]], 'amplitude': 2}],
        affine_terms=[{'anchor': [0, 0], 'vector': [3, -2]}])
    assert objective(0) == pytest.approx(2-.54)
    assert objective(math.pi) == pytest.approx(2*math.exp(-.36**2/.02)+.54)
    center[0] = 99  # The frozen snapshot does not follow later registry mutation.
    binding['sensor_transform'][0][3] = 99
    assert objective(0) == pytest.approx(2-.54)


def test_affine_first_harmonic_has_improvement_sign():
    objective = reference.augmented_objective(
        lambda *args: 0, base_xy=[2, 1], binding=_binding(), weights=[0, 0, 1],
        gaussian_fills=[], affine_terms=[{'anchor': [0, 0], 'vector': [3, -2]}])
    harmonic = _harmonics(objective)
    assert harmonic['coefficients']['cosine']['value'] == pytest.approx(-.54)
    assert harmonic['coefficients']['sine']['value'] == pytest.approx(.36)
    result = reference.stationary_reference(harmonic, omega_rad_sec=2)
    assert np.dot(result['world_vector'], [3, -2]) > 0


@pytest.mark.parametrize('change', ['mount', 'axis', 'joint', 'missing_objective'])
def test_unknown_geometry_or_objective_is_not_raw_substitution(change):
    binding, fills = _binding(), []
    if change == 'mount':
        binding['sensor_transform'][0][3] = .20
    if change == 'axis':
        binding['rotation_axis'] = [0, 1, 0]
    if change == 'joint':
        binding['joint_position_m'][0] = .01
    if change == 'missing_objective':
        fills = None
    with pytest.raises(ValueError):
        reference.augmented_objective(lambda *args: 0, base_xy=[0, 0], binding=binding,
                                      weights=[1, 1, 0], gaussian_fills=fills, affine_terms=[])


def test_cycle_rate_uses_world_observations_and_checks_uniform_sampling():
    stamps = [index*10_000_000 for index in range(301)]
    phases = [index*math.tau/300 for index in range(301)]
    result = reference.qualify_cycle_rates(stamps, phases)
    assert result['qualified'] and result['discrete_sensitivity_available']
    assert result['omega_rad_sec'] == pytest.approx(math.tau/3)
    phases[100] += .03
    result = reference.qualify_cycle_rates(stamps, phases)
    assert not result['qualified']
    assert result['reason'] == 'world_phase_reversal'


def test_rate_variation_and_nonuniform_cadence_are_distinct():
    stamps = [index*10_000_000+(1_000_000 if index % 2 else 0) for index in range(301)]
    phases = [stamp/3e9*math.tau for stamp in stamps]
    result = reference.qualify_cycle_rates(stamps, phases)
    assert result['qualified'] and not result['discrete_sensitivity_available']
    uniform_phases = [index*math.tau/300 for index in range(301)]
    assert not reference.qualify_cycle_rates(stamps, uniform_phases)['qualified']


def test_target_population_is_fixed_without_outcome_selection():
    targets = reference.select_reference_targets(4_000_000_000)
    assert len(targets) == 24
    assert targets[0] == 14_000_000_000 and targets[-1] == 244_000_000_000
    with pytest.raises(ValueError):
        reference.select_reference_targets(4.0)


def test_anchor_cannot_precede_target_even_when_publication_is_later():
    observations = [{'qualified': True, 'readiness_eligible': True,
                     'stamp_ns': 990_000_000, 'cost_stamp_ns': 1_010_000_000},
                    {'qualified': True, 'readiness_eligible': True,
                     'stamp_ns': 1_030_000_000, 'cost_stamp_ns': 1_040_000_000}]
    assert reference.select_causal_anchor(observations, 1_000_000_000) == 1
    assert reference.select_causal_anchor(observations[:1], 1_000_000_000) is None
    observations[1]['readiness_eligible'] = False
    assert reference.select_causal_anchor(observations, 1_000_000_000) is None


def test_actual_custom_filter_matches_uniform_discrete_stationary_reference():
    package = Path(__file__).resolve().parents[1] / 'ros_esc'
    config = json.loads((package / 'filter_node/filter_config_files/turtlebot_vehicle/'
                         'gradient_methods/gesc_filter_full_rotation.json').read_text())
    step = .01
    observations = [{'stamp_ns': index*10_000_000,
                     'cost': math.cos(index*step*math.tau/3),
                     'phase': index*step*math.tau/3, 'yaw_rad': 0.0}
                    for index in range(3601)]
    replay = reference.replay_custom_filter(observations, config,
                                            phase_field='phase', time_field='stamp_ns')
    actual = np.mean([item['world_vector'] for item in replay[-300:]], axis=0)
    target = reference.stationary_reference(_harmonics(math.cos), omega_rad_sec=math.tau/3,
                                             step_sec=step)
    assert actual == pytest.approx(target['discrete_sensitivity']['world_vector'], abs=1e-9)
    assert replay[0]['state_before'] == replay[0]['state_after']
    assert replay[1]['state_before'] == replay[0]['state_after']


def _matched_observations(count=501):
    values = []
    for index in range(count):
        stamp = index*30_000_000
        phase = index*math.tau/100
        values.append({'qualified': True, 'stamp_ns': stamp, 'cost_stamp_ns': stamp,
                       'cost': math.cos(phase), 'raw_cost': math.cos(phase),
                       'world_phase_rad': phase, 'projected_phase_rad': phase,
                       'latest_phase_rad': phase+.3, 'encoder_phase_rad': phase,
                       'yaw_rad': 0.0, 'xy': [0, 0], 'frame_id': 'odom',
                       'objective': {'weights': [1, 0, 0]}, 'objective_id': 'one',
                       'context_id': 0, 'pose_bracket_ns': [stamp, stamp],
                       'encoder_bracket_ns': [stamp, stamp], 'blend_allowed': True})
    return values


def test_reference_cycle_coverage_is_independent_of_three_cycle_confidence():
    observations = _matched_observations(102)
    first = reference.reference_cycle(observations, 101)
    assert first['qualified'] and first['input_coverage_valid']
    assert first['duration_sec'] == pytest.approx(3)
    assert first['actual_observation_count'] == 100
    assert first['discrete_sensitivity_available']
    assert reference.reference_cycle(observations, 99)['reason'] == 'incomplete_world_cycle'
    observations[60]['qualified'] = False
    assert reference.reference_cycle(observations, 101)['reason'] == 'cycle_context_discontinuity'


def test_reference_cycle_rejects_sparse_input_coverage():
    observations = _matched_observations(101)[::10]
    result = reference.reference_cycle(observations, len(observations)-1)
    assert not result['qualified']
    assert result['reason'] == 'insufficient_input_sector_coverage'


def test_reference_cycle_retains_first_boundary_arrival_and_plateau_dwell():
    observations = _matched_observations(101)
    plateau = []
    for index in range(11):
        item = deepcopy(observations[0])
        item['stamp_ns'] = index*30_000_000
        plateau.append(item)
    for item in observations[1:]:
        item['stamp_ns'] += 300_000_000
    values = plateau+observations[1:]
    result = reference.reference_cycle(values, len(values)-1)
    assert result['start_ns'] == 0
    assert result['duration_sec'] == pytest.approx(3.3)
    assert not result['qualified'] and result['reason'] == 'variable_world_rate'


def test_matched_replay_calls_actual_filter_and_rolling_owner_with_fallback():
    package = Path(__file__).resolve().parents[1] / 'ros_esc'
    config = json.loads((package / 'filter_node/filter_config_files/turtlebot_vehicle/'
                         'gradient_methods/gesc_filter_full_rotation.json').read_text())
    observations = _matched_observations()
    result = reference.replay_matched_direction(observations, config)
    assert not result[101]['blend_applied']  # One cycle remains in the denominator.
    assert result[-1]['blend_applied']
    assert not result[-1]['exact_transport_reconstruction']
    assert result[25]['legacy_world_vector'] != pytest.approx(result[25]['synchronized_instant_world_vector'])
    observations[-1]['blend_allowed'] = False
    disabled = reference.replay_matched_direction(observations, config)
    assert disabled[-1]['averaging_qualified'] and not disabled[-1]['blend_applied']
    assert disabled[-1]['v2_world_vector'] == disabled[-1]['synchronized_instant_world_vector']


def test_matched_replay_preserves_absent_output_after_runtime_phase_fault():
    package = Path(__file__).resolve().parents[1] / 'ros_esc'
    config = json.loads((package / 'filter_node/filter_config_files/turtlebot_vehicle/'
                         'gradient_methods/gesc_filter_full_rotation.json').read_text())
    observations = _matched_observations(3)
    observations[1]['world_phase_rad'] = math.pi
    observations[1]['projected_phase_rad'] = math.pi
    results = reference.replay_matched_direction(observations, config)
    assert not results[1]['output_valid']
    assert results[1]['v2_world_vector'] is None
    assert reference.angular_error_deg(results[1]['v2_world_vector'], [1, 0]) is None


def _retained_fixture():
    from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
    def record(message, absolute, *, source=None, receipt=None):
        return BagRecord('topic', 'fixture', round((absolute if receipt is None else receipt)*1e9),
                         round(absolute*1e9), absolute-9 if source is None else source, True,
                         message, True)
    def quaternion(yaw):
        return NS(x=0.0, y=0.0, z=math.sin(yaw/2), w=math.cos(yaw/2))
    times = [10+index*.025 for index in range(13)]
    poses = [record(NS(header=NS(frame_id='odom'), pose=NS(pose=NS(
        position=NS(x=0., y=0.), orientation=quaternion(.2)))), stamp) for stamp in times]
    encoders = [record(NS(data=[stamp-9]), stamp) for stamp in times]
    raw, transforms, breakdown = [], [], []
    for stamp in [10, 10.1, 10.2]:
        raw.append(record(NS(data=[-1.]), stamp+.02, receipt=stamp+.03))
        transforms.append(record(NS(transform_array=[NS(rotation=quaternion(stamp-9+.2))]),
                                 stamp, receipt=stamp+.001))
        breakdown.append(record(NS(raw_cost=[-1.], augmented_cost=[-1.], raw_cost_valid=True,
                                   augmented_cost_valid=True, weights_valid=True,
                                   sensor_weight=1., gaussian_weight=1., affine_weight=0.),
                                stamp+.03, source=stamp+.02-9, receipt=stamp+.04))
    aliases = {'pose': poses, 'encoder': encoders, 'raw_cost_legacy': raw,
               'sensor_transform': transforms, 'cost_breakdown': breakdown, 'gaussian_fills': [],
               'timekeeper': [record(NS(start_time=9., mode='sim time'), 9.)],
               'clock': [record(NS(clock=NS(sec=10, nanosec=0)), 10.)],
               'algorithm_state': [record(NS(state_valid=True, state=1, state_name='SEARCH',
                                             active_fill_count_valid=True, active_fill_count=0), 9.99)]}
    return BagData(Path('/unused'), {}, {name: {'topic': name} for name in aliases}, aliases,
                   round(9.9e9), None)


def test_retained_matching_keeps_projected_and_latest_phase_and_proxy_identity():
    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import prepare_v2_direction_replay_inputs
    observations, receipt = prepare_v2_direction_replay_inputs(_retained_fixture())
    assert receipt['qualified_sample_count'] == 3
    assert receipt['origin_ns'] == 10_020_000_000
    first = observations[0]
    assert first['stamp_ns'] == 10_000_000_000
    assert first['cost_stamp_ns'] == 10_020_000_000
    assert first['projected_phase_rad'] == pytest.approx(1.0)
    assert first['latest_phase_rad'] == pytest.approx(1.025)
    assert not first['exact_m2_source_provenance']
    assert first['objective']['complete_registry_proxy']


def test_retained_affine_without_actual_terms_is_unavailable_not_raw():
    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import prepare_v2_direction_replay_inputs
    bag = _retained_fixture()
    for record in bag.records_by_topic['cost_breakdown']:
        record.message.affine_weight = 1.
    observations, _ = prepare_v2_direction_replay_inputs(bag)
    assert all(item['qualified'] for item in observations)
    assert all(item['objective']['affine_terms'] is None for item in observations)


def test_reconstruction_availability_does_not_change_objective_law_identity():
    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import prepare_v2_direction_replay_inputs
    bag = _retained_fixture()
    old = bag.records_by_topic['algorithm_state'][0]
    message = deepcopy(old.message)
    message.active_fill_count = 1  # Evidence disagreement; no actual fill-law message.
    bag.records_by_topic['algorithm_state'].append(replace(
        old, message=message, bag_timestamp_ns=10_090_000_000, ros_timestamp_ns=10_090_000_000))
    observations, _ = prepare_v2_direction_replay_inputs(bag)
    assert observations[0]['objective']['complete_registry_proxy']
    assert not observations[1]['objective']['complete_registry_proxy']
    assert len({item['objective_id'] for item in observations}) == 1


def test_retained_regressing_encoder_is_not_sorted_into_valid_evidence():
    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import prepare_v2_direction_replay_inputs
    bag = _retained_fixture()
    bag.records_by_topic['encoder'].reverse()
    observations, receipt = prepare_v2_direction_replay_inputs(bag)
    assert observations == [] and not receipt['qualified']
    assert 'regression' in receipt['reason']


def test_retained_pose_brackets_cannot_be_extrapolated():
    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import prepare_v2_direction_replay_inputs
    bag = _retained_fixture()
    bag.records_by_topic['pose'] = bag.records_by_topic['pose'][1:]
    observations, _ = prepare_v2_direction_replay_inputs(bag)
    assert not observations[0]['qualified']
    assert 'bracket unavailable' in observations[0]['invalid_reason']


def test_exclusive_reference_receipt_cannot_overwrite_prior_attempt(tmp_path):
    from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
    path = tmp_path / 'anchor.json'
    atomic_exclusive_json(path, {'qualified': False})
    with pytest.raises(FileExistsError):
        atomic_exclusive_json(path, {'qualified': True})
    assert json.loads(path.read_text()) == {'qualified': False}


def test_recorded_launch_defaults_and_overrides_resolve_historical_sensor_owner():
    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import _v2_direction_recorded_settings
    xml = '''<launch>
      <arg name="sensor_transform_config_filepath" default="/historical/sensor.json"/>
      <arg name="cost_function_config_filepath" default="/historical/cost.json"/>
      <arg name="filter_config_filepath" default="/historical/filter.json"/>
      <arg name="algorithm_raw_cost_topic" default="/raw"/>
      <arg name="algorithm_pose_topic" default="/odom"/>
      <executable cmd="ros2 run ros_esc sensor_pose_node $(var sensor_transform_config_filepath)"/>
    </launch>'''
    metadata = {'target_argv': ['ros2', 'launch', 'turtlebot3_rotating_sensor', 'gazebo.launch.xml',
                                'filter_config_filepath:=/recorded/selected_filter.json']}
    result = _v2_direction_recorded_settings(metadata, xml)
    assert result['filter_config_filepath'] == '/recorded/selected_filter.json'
    assert result['sensor_transform_config_filepath'] == '/historical/sensor.json'
    with pytest.raises(ValueError, match='sensor transform owner'):
        _v2_direction_recorded_settings(metadata, xml.replace('sensor_pose_node', 'different_owner'))
    with pytest.raises(ValueError, match='duplicate'):
        metadata['target_argv'].append('filter_config_filepath:=/another.json')
        _v2_direction_recorded_settings(metadata, xml)


@pytest.mark.parametrize('capture', ['value_and_type', 'missing', 'conflicting_values', 'wrong_geometry'])
def test_recorded_binding_reads_parameter_values_without_type_metadata(
        tmp_path, monkeypatch, capture):
    import subprocess
    import yaml
    from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analyzer
    from ros_esc.scenario_runner import aggregate_field_truth as truth

    repository = tmp_path / 'repository'
    repository.mkdir()
    geometry = '''<robot name="fixture">
      <joint name="rotating_frame_joint" type="continuous">
        <origin xyz="0 0 0.355" rpy="0 0 0"/><axis xyz="0 0 1"/>
      </joint>
      <joint name="sensor_joint" type="fixed"><origin xyz="0.18 0 0.015" rpy="0 0 0"/></joint>
    </robot>'''
    geometry_path = repository / 'robot.urdf'
    geometry_path.write_text(geometry)
    sensor_path = repository / 'sensor.json'
    sensor_path.write_text(json.dumps({'rotating_frame_one': {
        'object_name': 'Transform_Odom_To_Sensor_Pose',
        'params': {'joint_position': [0, 0, .355], 'rotation_axis': [0, 0, 1],
                   'sensor_transform': _binding()['sensor_transform']}}}))
    model_path = repository / 'model.json'
    model_path.write_text('{}')  # Parsed/hash-checked only; no field model exists.
    package = Path(__file__).resolve().parents[1] / 'ros_esc'
    filter_path = repository / 'filter.json'
    filter_path.write_bytes((package / 'filter_node/filter_config_files/turtlebot_vehicle/'
                             'gradient_methods/gesc_filter_full_rotation.json').read_bytes())
    launch_path = repository / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    launch_path.parent.mkdir(parents=True)
    launch_path.write_text(f'''<launch>
      <arg name="sensor_transform_config_filepath" default="{sensor_path}"/>
      <arg name="cost_function_config_filepath" default="{model_path}"/>
      <arg name="filter_config_filepath" default="{filter_path}"/>
      <arg name="algorithm_raw_cost_topic" default="/raw"/>
      <arg name="algorithm_pose_topic" default="/odom"/>
      <executable cmd="ros2 run ros_esc sensor_pose_node $(var sensor_transform_config_filepath)"/>
    </launch>''')
    run = tmp_path / 'run'
    run.mkdir()
    (run / 'metadata.yaml').write_text(yaml.safe_dump({'target_argv': [
        'ros2', 'launch', 'turtlebot3_rotating_sensor', 'gazebo.launch.xml']}))
    captured_xml = geometry.replace('0.18 0 0.015', '0.20 0 0.015') if capture == 'wrong_geometry' else geometry
    node = {'available': True, 'parameter_services_exposed': True,
            'parameters': {'/robot_state_publisher_node': {'ros__parameters': {
                'robot_description': captured_xml}}},
            'parameter_types': {'robot_description': 'string'}}
    assert analyzer._find_parameter(node, 'robot_description') is None
    if capture == 'missing':
        node['parameters'] = {}
    if capture == 'conflicting_values':
        node['parameters']['/other'] = {'ros__parameters': {'robot_description': '<robot/>'}}
    (run / 'resolved_parameters.yaml').write_text(yaml.safe_dump({
        'nodes': {'/robot_state_publisher_node': node}, 'failures': []}))
    row = {'recorded_git': {'commit': 'fixture'}, 'run_directory': str(run),
           'parameter_file_provenance': [
               {'path': str(path), 'recorded_blob_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
               for path in (model_path, filter_path)]}
    def fake_git(argv, **kwargs):
        assert argv[:2] == ['git', 'show']
        relative = argv[2].split(':', 1)[1]
        return NS(stdout=(repository / relative).read_bytes())
    monkeypatch.setattr(subprocess, 'run', fake_git)
    monkeypatch.setattr(truth, 'SENSOR_GEOMETRY_PATH', geometry_path)
    if capture == 'value_and_type':
        result = analyzer._v2_direction_recorded_binding(row, repository)
        assert result['captured_robot_description_hashes'] == [hashlib.sha256(geometry.encode()).hexdigest()]
    else:
        with pytest.raises(ValueError, match='captured live'):
            analyzer._v2_direction_recorded_binding(row, repository)
